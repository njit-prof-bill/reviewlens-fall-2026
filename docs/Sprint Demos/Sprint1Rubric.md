# Sprint 1 Demo Grading Rubric (Fall 2026)

_ReviewLens AI - CS 490 Capstone_

## 1. Purpose and Scoring Model

This rubric is used to evaluate the Sprint 1 ReviewLens AI demonstration.

The student-facing `Sprint1Demo.md` document defines what teams are expected to prepare and demonstrate. This rubric is primarily an instructor scoring tool.

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
2. Design and architecture quality.
3. Ability to explain implementation decisions and tradeoffs.
4. Understanding of security responsibilities.
5. Understanding of testing strategy.
6. Ability to answer questions accurately and concisely.
7. Quality and organization of the presentation.
8. Evidence that multiple team members understand the system.

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

1. Crash, unhandled runtime error, or broken required flow.
2. Behavior that clearly contradicts a Sprint 1 requirement.
3. Required evidence that should exist but is unavailable when requested.
4. User-visible error handling that exposes raw exceptions, stack traces, database errors, provider errors, or other technical failure information that is not meaningful to an average application user.
5. A security or ownership rule that fails during a demonstrated negative test.
6. Ingestion that reports success while producing fabricated, clearly incorrect, or incorrectly associated review data.
7. A previously demonstrated valid workflow that breaks later in the same demo.

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

Readiness deductions may apply when required accounts, data, environment configuration, tests, CI evidence, security-demo inputs, or other expected demo prerequisites were not prepared in advance.

A third-party outage by itself is not a readiness problem when the team has prepared appropriate fallback evidence and continues the demo efficiently.

---

## 4. Objective Checklist

Score each item `0`, `1`, or `2`.

### A. Readiness, Authentication, and Protected Access

| ID | Criterion | Evidence to Observe | Sprint 1 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C01 | Sprint 1 application is operational when the demo begins | Application and required backend services are ready without substantial setup | S1-005, S1-008 |  |
| C02 | Managed authentication is correctly integrated | User A authenticates successfully through the selected identity provider and reaches protected ReviewLens functionality | S1-009 |  |
| C03 | Unauthenticated access to protected functionality is denied | Logged-out user cannot directly access protected ReviewLens UI and/or protected backend behavior | S1-010 |  |
| C04 | Logout terminates protected application access | After logout, the prior authenticated session cannot continue using protected functionality | S1-009, S1-010 |  |

### B. AnalysisTarget Behavior

| ID | Criterion | Evidence to Observe | Sprint 1 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C05 | User A has meaningful persisted AnalysisTarget data | Existing targets are visible after authentication and are clearly associated with User A | S1-011, S1-014, S1-017 |  |
| C06 | Invalid AnalysisTarget input is rejected correctly | Deliberately invalid input is rejected; meaningful user-facing validation appears; invalid target is not persisted | S1-016 |  |
| C07 | Valid AnalysisTarget creation works | Corrected input creates a new target associated with User A | S1-011, S1-014, S1-015 |  |
| C08 | AnalysisTarget persistence and reopening work | Target survives refresh/navigation and can be reopened from the target list/workspace | S1-014, S1-015, S1-017, S1-018 |  |
| C09 | AnalysisTarget workspace clearly identifies active context | Target/entity, platform, source reference, and ingestion path/state are visible and coherent | S1-018 |  |

### C. Review Ingestion and Persistence

| ID | Criterion | Evidence to Observe | Sprint 1 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C10 | Ingestion can be initiated for an owned AnalysisTarget | User A starts ingestion from a target they own | S1-019 |  |
| C11 | Application obtains real review data through the supported ingestion/import path | Team shows source-derived/imported review data rather than hard-coded fabricated demo records | S1-020 |  |
| C12 | Review normalization produces the required canonical data | Representative persisted Reviews include at least review text and rating | S1-021 |  |
| C13 | Ingested Reviews are persisted and associated with the correct AnalysisTarget | Review records remain available and are linked to the intended target after navigation/refresh | S1-022 |  |
| C14 | Ingestion result state is recorded and visible | Application clearly distinguishes successful ingestion from no ingestion or failed ingestion | S1-023 |  |
| C15 | Invalid or failed ingestion is handled safely | Failure produces meaningful user-facing behavior, does not fabricate success, and preserves existing valid data | S1-019, S1-020, S1-021, S1-023 |  |

### D. Cross-User Authorization

| ID | Criterion | Evidence to Observe | Sprint 1 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C16 | User B has a distinct authenticated account and distinct data | User B can authenticate and view only their normal account context | S1-009, S1-011, S1-017 |  |
| C17 | Direct cross-user AnalysisTarget access is denied by backend/persistence authorization | While authenticated as User B, team deliberately requests a known valid User A target URL/ID and access is denied | S1-012, S1-013 |  |

**For full credit on C17:** the team must deliberately request a known User A resource while authenticated as User B. Merely showing that User A's target does not appear in User B's list is not sufficient.

### E. Automated Testing and Continuous Integration

| ID | Criterion | Evidence to Observe | Sprint 1 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C18 | Representative negative automated tests exist and are understood | Team shows authentication/authorization, validation, and ingestion/normalization negative tests and explains what each protects against | S1-006, S1-010, S1-012, S1-013, S1-016, S1-019 to S1-023 |  |
| C19 | CI automatically runs required Sprint 1 quality gates | Recent workflow clearly includes lint/static checks, build, and automated tests | S1-006, S1-007 |  |
| C20 | Required CI checks protect the normal merge workflow | Team shows branch protection, required status checks, prior blocked PR, or equivalent evidence that failing required checks prevent normal merge | S1-007 |  |
