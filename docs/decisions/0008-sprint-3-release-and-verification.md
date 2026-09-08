# 0008 - Sprint 3 Release and Verification

Date: 2026-09-08
Status: Accepted

## Decision

The existing AWS `dev` environment is ReviewLens's production-equivalent
environment for the capstone. A successful `ci` workflow on protected `main`
triggers `deploy-dev` through `workflow_run`. The deployment workflow checks out
the CI workflow's exact commit SHA, runs the ECS migration task before the API
rollout, waits for ECS stability, publishes the frontend, and fails if health,
readiness, CORS, or authenticated smoke verification fails.

Manual `deploy-dev` dispatch is retained only for retry or recovery. It verifies
that the selected commit has a successful `release-gate` check before any AWS
deployment action.

## Verification

The post-deployment smoke suite signs in to the deployed Clerk application with
two dedicated test accounts. It verifies public availability, protected access,
database readiness, controlled review import and summary, grounded Q&A,
out-of-scope Q&A, and cross-user target denial. It creates and deletes only a
uniquely named temporary target owned by the smoke account.

## Consequences

- A failed CI gate cannot reach normal deployment.
- A failed migration, deploy, health, or smoke step fails the release visibly.
- Production-equivalent credentials stay in GitHub secrets or AWS Secrets
  Manager; the browser receives no server-side credentials.
- The environment can still be paused with `teardown-dev` after validation.
