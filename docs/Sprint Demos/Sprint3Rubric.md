# Sprint 3 Demo Grading Rubric (Fall 2026)

_ReviewLens AI - CS 490 Capstone_

## 1. Purpose and Scoring Model

This rubric is used to evaluate the Sprint 3 ReviewLens AI demonstration.

The student-facing `Sprint3Demo.md` defines what teams are expected to prepare and demonstrate. This rubric is primarily an instructor scoring tool.

### Objective Checklist

There are **20 objective checklist items**.

Each item is scored:

- **0 — Not demonstrated / substantially incorrect**
- **1 — Partially demonstrated / materially incomplete**
- **2 — Fully demonstrated / meets the requirement**

Objective subtotal:

`20 items × 2 points = 40 points maximum`

### Subjective Engineering and Presentation Score

Award **0 to 10 points** based on the complete demonstration.

Consider:

1. Technical understanding.
2. Production architecture and design quality.
3. Ability to explain deployment and operational tradeoffs.
4. Understanding of security and production configuration.
5. Understanding of reliability and failure handling.
6. Understanding of testing and release verification.
7. Ability to answer questions accurately and concisely.
8. Quality and organization of the presentation.
9. Evidence that multiple team members understand the production system.

Suggested scale:

- **0-2:** weak technical understanding
- **3-4:** limited understanding
- **5-6:** competent understanding
- **7-8:** strong technical reasoning
- **9-10:** excellent engineering understanding and presentation

Base score:

`Objective Checklist (0-40) + Subjective Score (0-10) = 50 points maximum before deductions`

---

## 2. Demo Bug / Fault Deductions

Subtract **1 point for each confirmed bug or fault** exposed during the demo.

There is no fixed cap.

A confirmed bug/fault includes:

1. Crash, unhandled runtime error, or broken required production flow.
2. Behavior that clearly contradicts a Sprint 1, Sprint 2, or Sprint 3 requirement.
3. Required production evidence that should exist but is unavailable when requested.
4. User-visible error handling that exposes raw exceptions, stack traces, credentials, provider errors, or other technical failure information not meaningful to an average user.
5. Production authentication or ownership protection that fails.
6. Production ingestion or Q&A behavior that fabricates successful results after an external-service failure.
7. Deletion or re-ingestion behavior that unexpectedly corrupts valid persisted data.
8. A release reported as successful even though required deployment or post-deployment verification failed.
9. A production regression in ingestion summary, grounded Q&A, scope guard, or user isolation.
10. A previously demonstrated valid workflow that breaks later in the same demo.

A deliberately demonstrated negative case is not a bug when the application handles the failure correctly.

---

## 3. Demo Readiness Deduction

Deduct **0 to 5 points** for avoidable lack of preparation.

- **0:** Fully prepared; no meaningful avoidable delays.
- **-1:** Minor preparation issue.
- **-2:** Noticeable preparation problems or unnecessary delays.
- **-3:** Significant preparation deficiencies consume meaningful demo time.
- **-4:** Major readiness problems prevent several required items from being demonstrated efficiently.
- **-5:** Team is substantially unprepared.

Readiness deductions may apply when the public environment, production accounts, persisted data, lifecycle targets, failure evidence, release evidence, health checks, smoke tests, security scans, migration evidence, or other expected production prerequisites were not prepared in advance.

A temporary third-party outage by itself is not a readiness problem when the deployed application handles it correctly and the team has prepared appropriate evidence.

---

## 4. Objective Checklist

Score each item `0`, `1`, or `2`.

### A. Production Deployment and Configuration

| ID | Criterion | Evidence to Observe | Sprint 3 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C01 | ReviewLens is publicly deployed and operational | Public production URL loads and protected production functionality is usable | S3-001, S3-020 |  |
| C02 | Production deployment is automated and gated by required checks | Recent release shows required CI gates completing before automated deployment from the protected release workflow | S3-001, S3-013 |  |
| C03 | Failed quality gates or deployment failures are visible and prevent a normal successful release | Prior failure evidence shows deployment is blocked or release failure is surfaced clearly | S3-013, S3-014 |  |
| C04 | Production configuration and secrets are separated and protected | Team shows masked/protected production configuration; server-side secrets are not committed or browser-exposed | S3-005, S3-006 |  |
| C05 | Persistence schema/migration compatibility is handled repeatably | Team shows migration/schema-management and release verification appropriate to its persistence technology | S3-015 |  |

### B. Production Lifecycle and Reliability

| ID | Criterion | Evidence to Observe | Sprint 3 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C06 | Returning user can reopen persisted production AnalysisTarget data | Earlier-session target, review data, ingestion state, and summary remain usable in production | S3-009 |  |
| C07 | User can delete an owned disposable AnalysisTarget safely | Deleted target is no longer normally accessible and associated-data behavior matches the documented persistence design | S3-010 |  |
| C08 | Cross-user destructive or resource access remains denied in production | User B cannot access/delete a known User A target; User A data remains intact | S3-011, S3-020 |  |
| C09 | Re-ingestion or approved equivalent lifecycle behavior is handled consistently | New ingestion state is distinguishable and valid existing data is protected, or approved equivalent behavior is demonstrated | S3-012 |  |
| C10 | Review ingestion/external-service failure is handled safely | Failure produces meaningful behavior, no fabricated success, protected diagnostics, and preserved valid data | S3-007 |  |
| C11 | LLM-provider failure is handled safely | Provider failure produces meaningful application behavior rather than fabricated analysis or raw provider errors | S3-008 |  |

### C. Complete Production ReviewLens Behavior

| ID | Criterion | Evidence to Observe | Sprint 3 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C12 | Production authentication and protected access still work | Public application requires authentication for protected ReviewLens behavior | S3-016, S3-020 |  |
| C13 | Production review data and ingestion summary remain correct | Controlled production target can access persisted reviews and expected summary behavior | S3-017, S3-020 |  |
| C14 | Production grounded Q&A works against the intended AnalysisTarget | In-scope production question receives a usable review-grounded response | S3-018, S3-020 |  |
| C15 | Production scope guard still rejects out-of-scope requests | Representative unrelated question is declined in the deployed application | S3-019, S3-020 |  |
| C16 | Multi-user production isolation remains intact | Production behavior and/or controlled evidence shows users cannot access one another's ReviewLens data or AI context | S3-020 |  |

### D. Post-Deployment Verification and Security

| ID | Criterion | Evidence to Observe | Sprint 3 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C17 | Automated health verification runs after deployment | Recent release includes health/readiness verification against the deployed application and failure is detectable | S3-002 |  |
| C18 | Automated production smoke-test suite verifies critical behavior safely | Smoke tests run against deployed/production-equivalent environment and are repeatable without corrupting real data | S3-003, S3-016, S3-017, S3-018, S3-019 |  |
| C19 | Security/dependency scanning is meaningful and reviewed | CI shows appropriate automated scanning and team can explain how significant findings are handled | S3-004 |  |
| C20 | Release pipeline provides end-to-end production verification | Recent release traces quality gates, deployment, health/smoke verification, and visible release outcome for the deployed commit | S3-001, S3-002, S3-003, S3-013, S3-014 |  |
