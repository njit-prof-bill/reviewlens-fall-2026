# Coding Standards

General standards:

- Prefer boring, explicit code.
- Keep domain logic out of route handlers.
- Keep API schemas separate from database models.
- Use clear names over clever abstractions.
- Add tests for reusable behavior.
- Avoid speculative generalization.

Python standards:

- Use type hints.
- Use Pydantic for API request and response schemas.
- Use SQLAlchemy for persistence models.
- Use service modules for business logic.

Frontend standards:

- Use React with TypeScript.
- Use functional components.
- Use shared layout components.
- Keep API access isolated from UI components.

## Repository layout

```
apps/api/app/
  routers/     one module per resource; HTTP concerns only
  services/    business logic; the only place that touches ownership rules
  db/models/   SQLAlchemy models, one per file, re-exported from __init__
  schemas/     Pydantic request/response models, re-exported from __init__
  domain.py    shared enums, status vocabulary, user-facing error messages
  errors.py    domain exceptions mapped to the API error envelope in main.py
  dependencies.py  get_current_user and the shared Annotated aliases

apps/web/src/
  components/ui/        vendored shadcn primitives; kept as generated
  components/analysis/  ReviewLens-specific composites built on those primitives
  components/layout/    app shell
  components/pages/     routed screens
  hooks/                react-query hooks; one per resource concern
  lib/api/              client, typed endpoint modules, shared types
```

## Naming

- Python: `snake_case` for functions and modules, `PascalCase` for classes.
  Service functions read as verbs: `create_target`, `get_owned_target`.
- TypeScript: `camelCase` for values, `PascalCase` for components and types.
  Component files match the component name.
- API fields stay `snake_case` on the wire in both directions, so the TypeScript
  interfaces in `lib/api/types.ts` mirror the Pydantic schemas exactly. Do not
  add a camelCase translation layer.

## Formatting and linting

Enforced by tooling, not by editor preference. CI runs all of these.

```
cd apps/api && ruff check app tests && ruff format --check app tests && pytest
cd apps/web && npm run lint && npm run typecheck && npm test && npm run build
```

Run `ruff format app tests` before committing Python.

## Layering rules

- Route handlers parse input, call one service function, and shape the response.
  No queries, no business rules.
- Service functions take a `Session` and an `owner_user_id` first. They own the
  ownership filter. See `ai-context/security-guardrails.md`.
- Models never import services. Services never import routers.
- `domain.py` holds vocabulary shared across layers so schemas do not import
  models to reach an enum.

## Error handling

- Services raise `AppValidationError` (422) or `ResourceNotFoundError` (404)
  from `app/errors.py`. Handlers in `main.py` render them into the standard
  envelope. Do not raise `HTTPException` from a service.
- `AppValidationError` carries `ApiErrorDetail(field=..., issue=...)` so the UI
  can attach the message to the right input.
- Every user-facing message is written for a non-technical reader. Technical
  detail goes to the log, never to the response.
- Long-running work records failure as state on a row rather than throwing past
  the caller. See `IngestionRun.error_code` and `error_message`.

## API response conventions

- Success returns the resource or `{"items": [...]}` for collections.
- Errors always return `{"error": {"code", "message", "details": []}}`.
- Resources are registered under both `/api/v1` and `/api`.
- Denial of someone else's resource returns 404, never 403.

## Logging

- Module-level `logger = logging.getLogger(__name__)`; no `print`.
- `logger.warning` for handled third-party failures, `logger.exception` for
  unexpected ones. Include the identifier under discussion.
- Never log tokens, API keys, or full request bodies.

## Adding dependencies

Prefer the standard library and what is already pinned. A new dependency needs a
reason a reviewer would accept, a check that it is maintained, and a pinned
version. Outbound HTTP on the backend uses `urllib.request`, matching
`clerk_profile.py` and `google_maps_provider.py`.

## Testing

- Backend tests live in `apps/api/tests`, frontend tests beside the component as
  `*.test.tsx`.
- Test observable behaviour. Name tests as sentences describing the guarantee.
- Anything user-scoped needs owner-succeeds, unauthenticated-denied, and
  cross-user-denied.
- Third-party calls are replayed from committed fixtures. No test touches the
  network.
- Inject collaborators (session factories, HTTP transports) rather than patching
  internals where practical.
