This document contains references to ReviewLens

# Deployment Validation

ReviewLens
is not intended to operate as a production application.

Deployment exists to validate:

- frontend build and hosting
- backend deployment
- database connectivity
- environment variable configuration
- authentication integration
- migrations
- health checks
- teardown

## Sprint 2 Q&A Validation

Before provisioning, run `infra/providers/aws/scripts/bootstrap-state.sh` to
create the OpenAI secret, then provide its ARN as `openai_api_key_arn`. Terraform
injects `OPENAI_API_KEY` only into API runtimes; it is not exposed to the frontend
or the ECS migration container. `LLM_PROVIDER` and `OPENAI_MODEL` are nonsecret
runtime values.

After deployment:

1. Confirm the ECS migration task applied the latest Alembic revision.
2. Authenticate and open a target with persisted reviews.
3. Submit one grounded question and verify evidence excerpts are returned.
4. Submit an unrelated question and verify an out-of-scope result.
5. Switch targets and verify the visible history and answer evidence change.
6. Confirm no raw OpenAI response, API key, or provider exception appears in an
   error response or CloudFront-delivered frontend asset.

CI does not call OpenAI. It uses the deterministic provider harness and enforces
80% changed-line coverage from API and web Cobertura reports.

Applications created from ReviewLens
may define their own production environment model.
