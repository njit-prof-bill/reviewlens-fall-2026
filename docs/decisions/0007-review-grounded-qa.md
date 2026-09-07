# 0007 - Review-Grounded Q&A

Date: 2026-09-05
Status: Accepted

## Context

Sprint 2 requires ReviewLens to answer questions from one authenticated user's
active AnalysisTarget, decline unrelated questions, report insufficient review
evidence, retain question history, and prove those boundaries without calling a
live language model in CI.

## Decision

Q&A is exposed as target-scoped REST resources:

- `POST /api/v1/analysis-targets/{target_id}/questions`
- `GET /api/v1/analysis-targets/{target_id}/questions`

Each request authorizes the target through `get_owned_target` and rebuilds a
bounded context from that target's persisted reviews. Context is ordered
deterministically and is not cached across requests. Sprint 2 does not introduce
embeddings or a vector database.

Language-model access uses an `LLMProvider` protocol. OpenAI is the first
adapter, selected by `LLM_PROVIDER`; orchestration and tests do not depend on the
OpenAI SDK. The provider must return structured output with one result kind:

- `grounded`
- `insufficient_evidence`
- `out_of_scope`

Grounded results must cite review IDs present in the supplied context. ReviewLens
rejects unknown IDs and snapshots cited excerpts when persisting an answer.
Non-grounded results cannot carry evidence. Provider failures create no history
entry and return a user-safe service-unavailable response.

Q&A entries inherit ownership through `AnalysisTarget`; owner IDs are not
duplicated on Q&A tables. Deleting a target cascades to its Q&A history. Evidence
keeps an immutable excerpt while its optional source review reference may become
null if reviews are replaced.

The version-controlled system prompt is the primary scope guard. Application
logic validates the structured result and evidence boundary but does not use a
question blacklist. A deterministic fake-provider test harness and a committed
scope evaluation set exercise the behavior in CI.

## Consequences

- Switching targets cannot retain server-side context because every request is
  rebuilt from the target ID in its route.
- Persisted notebook history remains intelligible after re-ingestion.
- Context is intentionally bounded by `QA_MAX_CONTEXT_CHARACTERS`; very large
  datasets will require retrieval improvements in a future sprint.
- Adding another provider requires a new adapter and factory branch, not changes
  to Q&A routing, persistence, or UI code.
