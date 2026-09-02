# Sprint 2 Demo Grading Rubric (Fall 2026)

_ReviewLens AI - CS 490 Capstone_

## 1. Purpose and Scoring Model

This rubric is used to evaluate the Sprint 2 ReviewLens AI demonstration.

The student-facing `Sprint2Demo.md` defines what teams are expected to prepare and demonstrate. This rubric is primarily an instructor scoring tool.

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
4. Understanding of AI grounding and scope boundaries.
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
2. Behavior that clearly contradicts a Sprint 1 or Sprint 2 requirement.
3. Required evidence that should exist but is unavailable when requested.
4. User-visible error handling that exposes raw exceptions, stack traces, provider errors, or other technical failure information not meaningful to an average user.
5. An ingestion summary that is materially inconsistent with persisted review data.
6. A grounded Q&A response that clearly claims review evidence not present in the active dataset.
7. A required scope guard that clearly fails.
8. Stale or wrong-target review context used after switching AnalysisTargets.
9. Cross-user review data entering another user's AI context.
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

Readiness deductions may apply when required datasets, prepared questions, test evidence, CI evidence, environment configuration, or other expected demo prerequisites were not prepared in advance.

Sprint 2 specifically requires the demo to run from the **randomly selected team member's development computer**. An incomplete selected environment is a readiness problem.

A temporary third-party or LLM outage by itself is not a readiness problem when the team has prepared appropriate evidence and continues the demo efficiently.

---

## 4. Objective Checklist

Score each item `0`, `1`, or `2`.

### A. Environment Readiness and Ingestion Summary

| ID | Criterion | Evidence to Observe | Sprint 2 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C01 | Randomly selected team member's development environment is operational | Selected device runs the current application and required services without substantial repair/setup | S2-001 to S2-004; Sprint 1 baseline |  |
| C02 | Active AnalysisTarget and ingestion state are clearly identified | Workspace clearly identifies target, source/platform, and relevant ingestion state | S2-005, S2-017 |  |
| C03 | Ingestion summary accurately reports review count and rating information | Displayed values are derived from persisted review data and can be plausibly verified | S2-006, S2-008 |  |
| C04 | Rejected/skipped records and result state are represented correctly when applicable | Failed/partial records are not silently counted as successful review data | S2-005, S2-007, S2-008 |  |

### B. Review-Grounded Q&A

| ID | Criterion | Evidence to Observe | Sprint 2 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C05 | Q&A interface supports a natural-language review question | User can submit a question and receive a ReviewLens response with clear active-target context | S2-009 |  |
| C06 | Active review dataset is supplied to the Q&A orchestration path | Team demonstrates or explains how persisted reviews for the active target become model context | S2-010 |  |
| C07 | In-scope question receives a useful answer grounded in review evidence | Team can identify representative review evidence supporting the answer | S2-011 |  |
| C08 | Unsupported information is not invented | Relevant question lacking evidence produces an explicit insufficiency response | S2-012 |  |

### C. Scope Guard

| ID | Criterion | Evidence to Observe | Sprint 2 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C09 | System prompt explicitly constrains ReviewLens to the active review dataset | Prompt or reviewable configuration establishes dataset, unsupported-information, and refusal boundaries | S2-013 |  |
| C10 | Unrelated general-knowledge question is declined | Prepared general-knowledge question receives a clear scope refusal | S2-014 |  |
| C11 | Other-entity or other-platform question is declined | Prepared question about data outside the active dataset receives a clear scope refusal | S2-015 |  |
| C12 | Scope guard is not merely a hard-coded demo-question blacklist | Team can explain prompt/context-based enforcement and show broader evaluation coverage | S2-013, S2-014, S2-015, S2-004 |  |

### D. Analysis Context and User Isolation

| ID | Criterion | Evidence to Observe | Sprint 2 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C13 | User can switch to another owned AnalysisTarget and active context is clear | UI, summary, and Q&A context visibly move to Target B | S2-017 |  |
| C14 | Q&A context changes when AnalysisTarget changes | Target B question is answered using Target B's distinctive review content | S2-018 |  |
| C15 | Stale Target A review context is not retained after switching | Team demonstrates or tests that prior-target reviews are excluded from subsequent Q&A | S2-019 |  |
| C16 | Cross-user review data is excluded from AI context | Controlled test/harness evidence shows another user's distinctive review content is not supplied to the model boundary | S2-016 |  |
| C17 | Target without successful review data cannot produce normal grounded Q&A | Empty/failed target is prevented from behaving as though review evidence exists, shown live or through direct automated evidence | S2-020 |  |

### E. Sprint 2 Quality-Assurance Ratchet

| ID | Criterion | Evidence to Observe | Sprint 2 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C18 | Changed-code coverage gate is implemented and enforced | CI shows the selected coverage policy/threshold and required gate | S2-001 |  |
| C19 | Critical integration tests and deterministic Q&A test harness are implemented | Team shows integration coverage plus controlled LLM-boundary testing that does not depend on exact live-model output | S2-002, S2-003 |  |
| C20 | Scope-guard evaluation set and Sprint 2 CI enforcement are implemented | Team shows accepted/rejected evaluation cases and a recent CI workflow running required Sprint 2 checks | S2-004; Sprint 2 CI/CD requirements |  |
