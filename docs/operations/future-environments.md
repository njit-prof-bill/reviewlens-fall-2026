# Future Environments Strategy (Documented, Not Yet Implemented)

This document defines the intended tag and branch strategy for environments beyond cloud `dev`.

Status: documented only. Staging and production workflow automation is not implemented yet.

## Planned Promotion Rules

- `main` branch merge: deploy cloud `dev`
- `v*.*.*-dev-*` tag: deploy cloud `dev`
- `v*.*.*-rc-*` tag: deploy `staging` (planned)
- `v*.*.*-prod-*` tag: deploy `production` (planned)

## Release Integrity Requirement

Production tags must reference the same commit that was validated in the corresponding release-candidate deployment.

In other words:

1. Deploy and validate RC commit in staging
2. Promote that exact commit to production via `v*.*.*-prod-*` tag
3. Do not retag a different commit as production for the same release line

## Why This Matters

- Reduces drift between tested and released artifacts
- Preserves auditability of release promotions
- Supports reproducible rollbacks and incident analysis

## Implementation Notes (Future)

When implemented, workflows should enforce:

- Environment-specific approval gates
- Required smoke/integration checks before promotion
- Tag-to-commit verification from RC to production
- Clear run summaries for artifact/image identifiers used in each environment

## ECS Express Migration Prompt

Use the following prompt when implementing the AWS container-platform migration.

> Migrate Locked On It's AWS backend deployment architecture from Amazon App Runner to Amazon ECS Express Mode.
>
> Context:
>
> - AWS announced that App Runner is no longer accepting new customers. The existing App Runner service may remain operational as a legacy deployment, but new AWS environments and future Cornerstone-derived applications must use ECS Express Mode.
> - Do not interrupt or delete the existing App Runner service during this work.
> - The current AWS deployment foundation already includes:
>   - ECR for backend images
>   - private Amazon RDS PostgreSQL
>   - Secrets Manager for `DATABASE_URL` and `CLERK_SECRET_KEY`
>   - SSM Parameter Store for `CLERK_JWKS_URL`, `CORS_ORIGINS`, and frontend build values
>   - S3 and CloudFront for the React frontend
>   - GitHub Actions OIDC authentication
>   - Terraform remote state in S3 with DynamoDB locking
>   - VPC networking, private subnets, and security groups
> - The FastAPI image is already containerized. It currently packages Alembic and runs migrations before Uvicorn starts because GitHub-hosted runners cannot reach private RDS.
>
> Goals:
>
> 1. Add an ECS Express Mode backend implementation in Terraform without replacing the existing App Runner deployment initially.
> 2. Reuse the existing ECR repository, private RDS instance, Secrets Manager entries, SSM parameters, VPC, private subnets, CloudFront distribution, S3 bucket, and GitHub OIDC deployment role wherever practical.
> 3. Create an ECS Express service that:
>    - runs the FastAPI API container in private subnets,
>    - exposes a stable HTTPS API endpoint appropriate for CloudFront-hosted frontend use,
>    - receives `DATABASE_URL`, `CLERK_SECRET_KEY`, `CLERK_JWKS_URL`, `CORS_ORIGINS`, and optional Clerk issuer/audience values through existing AWS secret/parameter infrastructure,
>    - has health checks for `/api/v1/health`,
>    - uses least-privilege task execution and task roles,
>    - can reach private RDS on PostgreSQL port `5432`.
> 4. Replace migration-on-API-startup with a one-off ECS migration task:
>    - run `alembic upgrade head` from the same VPC/subnets/security groups as the API task,
>    - wait for migration completion,
>    - fail the deployment if the migration task fails,
>    - deploy or update the API service only after a successful migration,
>    - ensure only one migration task runs for each deployment.
> 5. Update the GitHub Actions deployment workflow:
>    - build and push a SHA-tagged backend image,
>    - run the ECS migration task,
>    - update the ECS service to that exact SHA-tagged image,
>    - wait for ECS service stability,
>    - publish frontend assets to the existing S3 bucket,
>    - invalidate the existing CloudFront distribution,
>    - update the frontend's `VITE_API_BASE_URL` only when the ECS endpoint is verified,
>    - run health, readiness, version, CORS, and frontend smoke tests.
> 6. Keep the existing App Runner workflow and resources operational until ECS is verified in parallel.
> 7. Add an explicit cutover mechanism:
>    - default to the existing App Runner API endpoint,
>    - allow an intentional workflow/configuration change to select the ECS API endpoint,
>    - document rollback to App Runner without rebuilding the frontend from scratch.
> 8. After parallel validation succeeds, add a separate, manually approved retirement path for App Runner. Do not retire App Runner automatically.
>
> Required engineering constraints:
>
> - Inspect and extend existing Terraform modules and workflow conventions; do not introduce a parallel naming, tagging, secret, or environment-variable scheme.
> - Keep the backend image compatible with local Docker development.
> - Do not expose RDS publicly.
> - Do not print secrets or connection strings in workflow logs, task logs, exceptions, or deployment summaries.
> - Do not rely on `Base.metadata.create_all()` as a deployment migration mechanism. Alembic must be authoritative.
> - Handle existing legacy databases that may have tables created before Alembic version tracking. Provide an explicit, reviewed baseline/stamping procedure rather than guessing at runtime.
> - Use semantic Terraform outputs for ECS endpoint, cluster/service/task identifiers, security groups, and migration task configuration.
> - Preserve existing frontend deployment behavior, Clerk configuration, CORS reconciliation, and Terraform state conventions.
> - Do not modify Daily Planning, Weekly Review, Execute domain behavior, or unrelated frontend code.
>
> Suggested implementation areas:
>
> - `infra/providers/aws/terraform/modules/ecs/`
> - `infra/providers/aws/terraform/environments/dev/`
> - `.github/workflows/deploy-dev.yml`
> - a new migration-task workflow or a clearly separated migration job within deployment
> - `apps/api/Dockerfile`
> - `apps/api/alembic/`
> - `apps/api/scripts/`
> - `docs/operations/cloud-development.md`
> - `docs/operations/future-environments.md`
> - `docs/decisions/0004-iaas-refactor.md`
> - `docs/development-logs/9-iaas-refactor.txt`
>
> Acceptance criteria:
>
> 1. Terraform can plan and apply ECS Express resources without modifying or destroying the existing App Runner service.
> 2. An ECS task can connect to private RDS using the existing secret/configuration path.
> 3. The migration task runs exactly once per deployment and applies Alembic migrations before API rollout.
> 4. The ECS API service becomes healthy at `/api/v1/health`.
> 5. The frontend can call the ECS API with valid CORS headers.
> 6. GitHub Actions reports the exact backend image SHA and ECS deployment target.
> 7. The existing App Runner service remains available until an explicit cutover.
> 8. A documented rollback can restore the frontend to App Runner.
> 9. The ECS API path is smoke-tested for `/api/v1/health`, `/api/v1/ready`, `/api/v1/version`, authenticated `/api/me`, and the Execute endpoints.
> 10. CI, Terraform validation, backend tests, frontend typecheck/lint/build, and deployment smoke tests pass.
>
> Before editing, inspect the current App Runner Terraform module, deploy workflow, Dockerfile, migration runner, AWS secret/SSM wiring, security groups, and operational documents. Present a file-specific implementation plan before making infrastructure changes.
