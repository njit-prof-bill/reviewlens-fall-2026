# Deployed Smoke Tests

`deploy-dev` runs `apps/web/scripts/deployed-smoke.mjs` after frontend publish,
CloudFront invalidation, ECS stability, health, readiness, version, and CORS
checks. A smoke failure fails the release workflow.

## Required GitHub Secrets

- `SMOKE_TEST_EMAIL`
- `SMOKE_TEST_PASSWORD`
- `SMOKE_ISOLATION_EMAIL`
- `SMOKE_ISOLATION_PASSWORD`

The runner logs in through the deployed Clerk sign-in page and obtains
short-lived session tokens through Clerk's browser API. It never prints tokens
or passwords.

## Assertions

- Public frontend, health endpoint, and database-backed readiness endpoint work.
- A protected endpoint rejects anonymous access.
- Smoke User creates a uniquely named target, imports the controlled CSV,
  verifies its summary, receives grounded Q&A with evidence, and receives an
  out-of-scope Q&A result.
- Isolation User receives 404 when accessing the Smoke User target.
- The runner deletes only its temporary target in `finally`, including related
  reviews, ingestion runs, Q&A entries, and evidence through target cascade.

## Diagnosing Failure

Check the release workflow step first. Health/readiness failures indicate API or
database availability; Clerk browser failures indicate smoke credentials or
Clerk configuration; Q&A failures indicate OpenAI/prompt/provider configuration;
and import failures indicate the deployed upload/ingestion path. Review ECS API
and migration CloudWatch log groups without copying secret values into tickets.
