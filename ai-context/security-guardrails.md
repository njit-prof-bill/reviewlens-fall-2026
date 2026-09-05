# Data and Security Guardrails

Authoritative for ReviewLens ownership boundaries, authentication assumptions,
authorization enforcement, and secret handling. Read this before writing any
query or mutation that touches user data.

## 1. Identity provider

Clerk is the managed identity provider. ReviewLens does not implement password
storage, credential verification, session issuance, or password reset.

- The frontend uses `@clerk/clerk-react`. Only `VITE_CLERK_PUBLISHABLE_KEY`
  reaches the browser, and it is designed by Clerk to be public.
- The backend verifies every protected request itself, in `app/auth.py`. Tokens
  are RS256, verified against Clerk's JWKS, with issuer and audience checked when
  configured. A request with no bearer token is rejected before anything else.
- `CLERK_SECRET_KEY` is server-side only. It is used solely to backfill profile
  fields Clerk omits from token claims.

## 2. Provider identity maps to one local user

The Clerk `sub` claim is stored as `users.auth_provider_user_id` (unique). The
mapping happens in exactly one place:

- `app.services.identity.bootstrap_user_from_identity` creates the local `User`
  on first authenticated request.
- `app.dependencies.get_current_user` wraps it and is the **only** trusted source
  of ownership.

Routes take `user: CurrentUser` and pass `user.id` into the service layer. A
route must never read an owner id from the request body, a query parameter, a
header, or a path segment.

## 3. User-scoped entities

| Entity           | How ownership is established              |
| ---------------- | ----------------------------------------- |
| `User`           | Is the owner                              |
| `AnalysisTarget` | `owner_user_id` foreign key to `users.id` |
| `Review`         | Inherited through `analysis_target_id`    |
| `IngestionRun`   | Inherited through `analysis_target_id`    |

`Workspace` and `WorkspaceMember` survive from the Cornerstone template and are
**not** part of the ownership chain. Do not authorize against them.

Reviews and ingestion runs deliberately do not duplicate an owner column. The
single path to them is through a target the caller already proved they own,
which means there is one rule to get right instead of three.

## 4. Where authorization is enforced

In the service layer, never in the router and never in the browser.

`analysis_target_service.get_owned_target(session, owner_user_id, target_id)` is
the chokepoint. It filters on `id` **and** `owner_user_id` in a single query and
raises `ResourceNotFoundError` when either fails to match.

Every child-resource operation calls it first, before parsing a file, before
contacting the review provider, and before reading or writing any review.

```
# Correct
target = analysis_target_service.get_owned_target(db, user.id, target_id)
reviews = review_service.list_reviews(db, target.id, limit, offset)

# Wrong: authorization by omission
target = db.get(AnalysisTarget, target_id)
if target.owner_user_id != user.id:
    ...
```

Similarly `review_service.get_owned_run` joins to `analysis_targets` and filters
on the owner, so an ingestion run id is never enough on its own.

## 5. Client-supplied identifiers are never trusted

A caller may know or guess another user's target id. That is expected and is not
a vulnerability by itself; the id is a locator, not a credential.

`POST /analysis-targets` accepts only `name` and `source_url`. Any extra field in
the body, including `owner_user_id`, is ignored by the Pydantic schema. This is
covered by a regression test that submits User B's id while authenticated as
User A and asserts the row belongs to User A.

## 6. Cross-user denial returns 404, not 403

A 403 confirms the resource exists. Every owner-scoped lookup returns
`ResourceNotFoundError` so a caller cannot distinguish "belongs to someone else"
from "does not exist". The UI mirrors this with a single calm message rather
than an error state.

## 7. Errors must not leak

- `app/main.py` installs an unhandled-exception handler returning a fixed
  message. Tracebacks never reach a response body.
- Ingestion failures carry a stable `error_code` plus a message drawn from
  `INGESTION_ERROR_MESSAGES` in `app/domain.py`. Provider text, HTTP status
  lines, and API keys are logged server-side and never persisted to the run or
  returned to the client.
- On the frontend, `lib/api/client.ts` maps any response that is not a valid
  error envelope onto a generic message, and `components/ErrorBoundary.tsx`
  catches render failures.

## 8. Secrets and configuration

- Real secrets never enter source control. `.env.example` and
  `apps/api/.env.example` document names only.
- `REVIEW_PROVIDER_API_KEY` is server-side. The browser never contacts the
  review provider; it only ever talks to the ReviewLens API.
- Anything prefixed `VITE_` is compiled into the bundle and is public by
  definition. Only the Clerk publishable key and the API base URL belong there.
- In deployed environments, values come from SSM Parameter Store and Secrets
  Manager as described in `iaas-standards.md`.

## 9. How cross-user isolation is tested

`apps/api/tests/conftest.py` provides `user_a`, `user_b`, and `client_factory`.
`client_factory(user)` overrides `get_current_user`; `client_factory()` leaves it
unset so the real authentication dependency rejects the request.

Every user-scoped feature needs all three:

1. The owner succeeds.
2. The unauthenticated caller is rejected, and the response body contains none
   of the protected data.
3. User B is denied on User A's resource, for reads **and** writes, and User A's
   data is unchanged afterwards.

See `test_analysis_targets.py::TestCrossUserAuthorization` and
`test_ingestion_endpoints.py::TestCrossUserIngestionAuthorization`.

## 10. Checklist for a new user-scoped endpoint

- [ ] The handler takes `user: CurrentUser`.
- [ ] The owner id comes from `user.id`, never from the request.
- [ ] The first service call is `get_owned_target` (or an equally scoped query).
- [ ] The query filters on the owner rather than filtering results afterwards.
- [ ] Denial produces 404.
- [ ] Errors return a user-safe message.
- [ ] Tests cover owner-succeeds, unauthenticated-denied, and cross-user-denied.
