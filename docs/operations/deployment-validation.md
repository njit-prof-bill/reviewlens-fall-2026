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

## Sprint 3 Public Demo Validation

Sprint 3 does not require a new deployment architecture. Use the existing ECS
backend and CloudFront frontend deployment path, then validate the complete
workflow from the public CloudFront URL.

Before the demo clock starts, confirm:

1. User A and User B can authenticate against the cloud-dev Clerk app.
2. User A has at least two saved analyses, including one created in an earlier session.
3. The primary User A analysis has a current review dataset with enough real reviews for evidence-backed Q&A.
4. Q&A history is visible after reopening the analysis.
5. Save As creates a separate analysis identity with copied current reviews and empty Q&A history.
6. Refresh/re-ingestion updates the current dataset without duplicate source reviews.
7. A failed refresh test proves the last known-good dataset is preserved.
8. Review browsing filters by rating and date remain scoped to the active analysis.
9. CSV and Markdown exports download with meaningful filenames and contain only owned data.
10. User B receives a not-found response when deliberately requesting User A's known analysis URL or id.

Representative pre-demo test evidence should include saved-analysis lifecycle,
Q&A history, duplicate-prevention or failed-refresh preservation, evidence
association, export ownership/content, and a recent successful CI run.
