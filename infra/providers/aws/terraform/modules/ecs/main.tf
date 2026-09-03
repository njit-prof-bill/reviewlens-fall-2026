variable "name_prefix" { type = string }
variable "environment" { type = string }
variable "ecr_repository_url" { type = string }
variable "ecr_image_tag" { type = string }
variable "vpc_id" { type = string }
variable "public_subnet_ids" { type = list(string) }
variable "private_subnet_ids" { type = list(string) }
variable "task_security_group_id" { type = string }
variable "clerk_secret_key_arn" {
  type      = string
  sensitive = true
}
variable "database_url_arn" {
  type      = string
  sensitive = true
}
variable "clerk_jwks_url_param_arn" { type = string }
variable "cors_origins_param_arn" { type = string }
variable "clerk_issuer_param_arn" { type = string }
variable "clerk_audience_param_arn" { type = string }
variable "desired_count" {
  type    = number
  default = 0
}

locals {
  container_name = "api"
  image_uri      = "${var.ecr_repository_url}:${var.ecr_image_tag}"
  api_secrets = [
    { name = "CLERK_SECRET_KEY", valueFrom = var.clerk_secret_key_arn },
    { name = "DATABASE_URL", valueFrom = var.database_url_arn },
    { name = "CLERK_JWKS_URL", valueFrom = var.clerk_jwks_url_param_arn },
    { name = "CORS_ORIGINS", valueFrom = var.cors_origins_param_arn },
  ]
  optional_clerk_secrets = concat(
    var.clerk_issuer_param_arn != "" ? [
      { name = "CLERK_ISSUER", valueFrom = var.clerk_issuer_param_arn },
    ] : [],
    var.clerk_audience_param_arn != "" ? [
      { name = "CLERK_AUDIENCE", valueFrom = var.clerk_audience_param_arn },
    ] : [],
  )
  container_secrets = concat(
    local.api_secrets,
    local.optional_clerk_secrets,
  )
}

output "cluster_arn" { value = aws_ecs_cluster.main.arn }
output "cluster_name" { value = aws_ecs_cluster.main.name }
output "service_arn" { value = aws_ecs_service.api.id }
output "service_name" { value = aws_ecs_service.api.name }
output "api_task_definition_arn" { value = aws_ecs_task_definition.api.arn }
output "migration_task_definition_arn" { value = aws_ecs_task_definition.migration.arn }
output "task_security_group_id" { value = var.task_security_group_id }
output "load_balancer_dns_name" { value = aws_lb.api.dns_name }
output "target_group_arn" { value = aws_lb_target_group.api.arn }

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.name_prefix}/api"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "migration" {
  name              = "/ecs/${var.name_prefix}/migration"
  retention_in_days = 14
}

resource "aws_ecs_cluster" "main" {
  name = "${var.name_prefix}-ecs"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_security_group" "load_balancer" {
  name_prefix = "${var.name_prefix}-ecs-alb-"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [var.task_security_group_id]
  }
}

resource "aws_security_group_rule" "task_from_load_balancer" {
  type                     = "ingress"
  from_port                = 8000
  to_port                  = 8000
  protocol                 = "tcp"
  security_group_id        = var.task_security_group_id
  source_security_group_id = aws_security_group.load_balancer.id
}

resource "aws_lb" "api" {
  name               = substr(replace("${var.name_prefix}-ecs", "_", "-"), 0, 32)
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.load_balancer.id]
  subnets            = var.public_subnet_ids
}

resource "aws_lb_target_group" "api" {
  name_prefix = "ecs-"
  port        = 8000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    path                = "/api/v1/health"
    matcher             = "200"
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "api" {
  load_balancer_arn = aws_lb.api.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}

resource "aws_iam_role" "execution" {
  name_prefix = "${var.name_prefix}-ecs-execution-"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "execution" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "execution_configuration" {
  name_prefix = "${var.name_prefix}-ecs-config-"
  role        = aws_iam_role.execution.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["secretsmanager:GetSecretValue", "ssm:GetParameter", "ssm:GetParameters"]
      Resource = [
        var.clerk_secret_key_arn,
        var.database_url_arn,
        var.clerk_jwks_url_param_arn,
        var.cors_origins_param_arn,
        var.clerk_issuer_param_arn,
        var.clerk_audience_param_arn,
      ]
    }]
  })
}

resource "aws_iam_role" "task" {
  name_prefix        = "${var.name_prefix}-ecs-task-"
  assume_role_policy = aws_iam_role.execution.assume_role_policy
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${var.name_prefix}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn
  container_definitions = jsonencode([{
    name         = local.container_name
    image        = local.image_uri
    essential    = true
    portMappings = [{ containerPort = 8000, protocol = "tcp" }]
    secrets      = local.container_secrets
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.api.name
        awslogs-region        = data.aws_region.current.region
        awslogs-stream-prefix = "api"
      }
    }
  }])
}

resource "aws_ecs_task_definition" "migration" {
  family                   = "${var.name_prefix}-migration"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn
  container_definitions = jsonencode([{
    name      = "migration"
    image     = local.image_uri
    essential = true
    command   = ["alembic", "upgrade", "head"]
    secrets   = local.container_secrets
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.migration.name
        awslogs-region        = data.aws_region.current.region
        awslogs-stream-prefix = "migration"
      }
    }
  }])
}

data "aws_region" "current" {}

resource "aws_ecs_service" "api" {
  name            = "${var.name_prefix}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.task_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = local.container_name
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.api]
}