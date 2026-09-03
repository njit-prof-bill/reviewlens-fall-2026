output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = module.frontend.cloudfront_domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (for invalidations)"
  value       = module.frontend.cloudfront_distribution_id
}

output "s3_bucket_name" {
  description = "S3 bucket name for frontend"
  value       = module.frontend.s3_bucket_name
}

output "app_runner_service_url" {
  description = "App Runner service URL"
  value       = module.backend.app_runner_service_url
}

output "app_runner_service_arn" {
  description = "App Runner service ARN"
  value       = module.backend.app_runner_service_arn
}

output "app_runner_role_arn" {
  description = "App Runner IAM execution role ARN"
  value       = module.backend.app_runner_role_arn
}

output "ecr_repository_url" {
  description = "ECR repository URL for Docker images"
  value       = module.backend_ecr.repository_url
}

output "ecs_service_url" {
  description = "HTTPS API base URL served through CloudFront"
  value       = "https://${module.frontend.cloudfront_domain_name}"
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "ECS API service name"
  value       = module.ecs.service_name
}

output "ecs_api_task_definition_arn" {
  description = "ECS API task definition ARN"
  value       = module.ecs.api_task_definition_arn
}

output "ecs_migration_task_definition_arn" {
  description = "ECS migration task definition ARN"
  value       = module.ecs.migration_task_definition_arn
}

output "ecs_task_security_group_id" {
  description = "Security group for ECS API and migration tasks"
  value       = module.ecs.task_security_group_id
}

output "ecs_load_balancer_dns_name" {
  description = "Internal ECS API load balancer hostname"
  value       = module.ecs.load_balancer_dns_name
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = module.database.rds_endpoint
  sensitive   = true
}

output "rds_port" {
  description = "RDS PostgreSQL port"
  value       = module.database.rds_port
}

output "rds_database_name" {
  description = "RDS database name"
  value       = module.database.rds_database_name
}

output "rds_security_group_id" {
  description = "RDS security group ID (for updating inbound rules)"
  value       = module.database.rds_security_group_id
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "public_subnets" {
  description = "Public subnet IDs"
  value       = module.networking.public_subnet_ids
}

output "private_subnets" {
  description = "Private subnet IDs"
  value       = module.networking.private_subnet_ids
}

output "database_url_secret_arn" {
  description = "ARN of DATABASE_URL secret in Secrets Manager"
  value       = var.rds_database_url_arn
  sensitive   = true
}

output "clerk_secret_key_arn" {
  description = "ARN of CLERK_SECRET_KEY secret in Secrets Manager"
  value       = var.clerk_secret_key_arn
  sensitive   = true
}

output "ssm_parameters" {
  description = "Map of SSM Parameter Store parameter names and their values"
  value = {
    "clerk_jwks_url"             = module.secrets.ssm_clerk_jwks_url
    "cors_origins"               = module.secrets.ssm_cors_origins
    "vite_api_base_url"          = module.secrets.ssm_vite_api_base_url
    "vite_clerk_publishable_key" = module.secrets.ssm_vite_clerk_publishable_key
  }
  sensitive = true
}

output "deployment_summary" {
  description = "Summary of deployed resources for next steps"
  sensitive   = true
  value       = <<-EOT

    ✓ Deployment Complete

    Frontend URL: https://${module.frontend.cloudfront_domain_name}
    App Runner URL: ${var.enable_app_runner ? module.backend.app_runner_service_url : "not managed"}
    ECS API URL:    https://${module.frontend.cloudfront_domain_name}
    Database:     ${module.database.rds_endpoint}

    Next Steps:
    1. Update Clerk Dashboard with these URLs:
       - Allowed Origins: https://${module.frontend.cloudfront_domain_name}
       - Redirect URLs: https://${module.frontend.cloudfront_domain_name}/sign-in
                        https://${module.frontend.cloudfront_domain_name}/sign-up
    2. Push to main branch to trigger deployment
    3. Monitor GitHub Actions for build/deploy progress

    Configuration Files:
    - Backend runtime configuration: SSM Parameter Store
    - Secrets: AWS Secrets Manager
  EOT
}
