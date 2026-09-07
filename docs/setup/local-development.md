# Local Development

Local development should run with:

- frontend dev server
- backend API server
- local PostgreSQL container

The local PostgreSQL instance is managed through Docker Compose.

Start the database:

```bash
./scripts/dev-db-up.sh
```

Stop the database:

```bash
./scripts/dev-db-down.sh
```

Reset the database:

```bash
./scripts/dev-db-reset.sh
```

Authentication setup:

- Follow [Authentication Setup (Clerk)](./authentication.md) before running login and registration flows locally.

## Sprint 2 Review Q&A

Add these server-side values to `apps/api/.env` or the repository `.env.local`:

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4.1-mini
LLM_TIMEOUT_SECONDS=30
QA_MAX_CONTEXT_CHARACTERS=60000
```

Never prefix the API key with `VITE_`; frontend build variables are public.

Apply the Sprint 2 schema and start the normal API/web processes:

```bash
cd apps/api
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
```

Useful validation commands:

```bash
# API tests and coverage
cd apps/api
pytest --cov=app --cov-report=xml
diff-cover coverage.xml --compare-branch=origin/main --fail-under=80

# Web tests and coverage
cd apps/web
npm run test:coverage
../api/.venv/bin/diff-cover coverage/cobertura-coverage.xml \
	--compare-branch=origin/main --fail-under=80
```

The Q&A endpoints are:

- `POST /api/v1/analysis-targets/{target_id}/questions`
- `GET /api/v1/analysis-targets/{target_id}/questions`

### Sprint 2 Demo Data

Prepare three real review exports with clearly different language, then run from
the repository root:

```bash
apps/api/.venv/bin/python scripts/seed_demo_data.py \
	--user-a-clerk-id user_a_id --user-a-email user-a@example.com \
	--user-b-clerk-id user_b_id --user-b-email user-b@example.com \
	--user-a-reviews ~/demo/target-a.json \
	--user-a-second-reviews ~/demo/target-b.json \
	--user-b-reviews ~/demo/user-b-private.json
```

The command is idempotent. It creates two populated targets and one empty target
for User A, plus an isolated populated target for User B. Know the expected
count, average rating, and rejection reasons for each imported file before the
demo.

Rehearse these categories before class:

1. A grounded question supported by Target A.
2. A relevant question absent from the reviews.
3. A general-knowledge question.
4. A question about another entity or platform.
5. A question whose answer contains Target A's distinctive evidence.
6. A question whose answer contains Target B's distinctive evidence after the switch.

The deterministic scope cases used by CI are in
`apps/api/tests/fixtures/qa_scope_cases.json`.
