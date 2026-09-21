# Sprint 3 Demo Grading Rubric (Fall 2026)

_ReviewLens AI - CS 490 Capstone_

## 1. Purpose and Scoring Model

This rubric is used to evaluate the Sprint 3 ReviewLens AI demonstration.

The student-facing Sprint 3 demo requirements define what teams are expected to prepare and demonstrate. This rubric is primarily an instructor scoring tool.

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
4. Understanding of persistence and lifecycle behavior.
5. Understanding of Q&A evidence and ownership boundaries.
6. Understanding of re-ingestion and failure safety.
7. Ability to answer questions accurately and concisely.
8. Quality and organization of the presentation.
9. Evidence that multiple team members understand the completed system.

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
2. Behavior that clearly contradicts a Sprint 1, Sprint 2, or Sprint 3 requirement.
3. Required evidence that should exist but is unavailable when requested.
4. User-visible error handling that exposes raw exceptions, stack traces, provider errors, or other technical failure information not meaningful to an average user.
5. Saved-analysis behavior that unexpectedly changes or corrupts another analysis.
6. Q&A history that appears under the wrong analysis.
7. Re-ingestion that duplicates reviews incorrectly, replaces valid data after a failed refresh, or leaves the active dataset ambiguous.
8. Supporting evidence that does not belong to the active AnalysisTarget or does not correspond to persisted review data.
9. Export that includes incorrect, stale, or cross-user data.
10. Public deployment behavior that differs materially from the required completed ReviewLens workflow.

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

Readiness deductions may apply when required production accounts, saved analyses, Q&A history, review data, refresh inputs, export evidence, tests, CI evidence, or other expected demo prerequisites were not prepared in advance.

A temporary third-party review-source or LLM outage by itself is not a readiness problem when the team has prepared appropriate fallback evidence and continues the demo efficiently.

---

## 4. Objective Checklist

Score each item `0`, `1`, or `2`.

### A. Saved Analysis Lifecycle

| ID | Criterion | Evidence to Observe | Sprint 3 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C01 | User can name and save an analysis | Analysis has a human-readable name distinct from the source URL and appears correctly in the analysis sidebar | S3-001 |  |
| C02 | User can rename a saved analysis | Name changes without altering source URL, review dataset, or other analysis state | S3-002 |  |
| C03 | Save As creates an independent analysis | Copy has a separate identity; changes to the copy do not mutate the original | S3-003 |  |
| C04 | Returning user can reopen a saved analysis | Earlier-session analysis restores source context, current review dataset, ingestion state, and summary | S3-004 |  |
| C05 | User can delete an owned analysis safely | Deletion requires clear intent, removes the analysis from normal retrieval, and preserves ownership enforcement | S3-005 |  |

### B. Persistent Q&A History

| ID | Criterion | Evidence to Observe | Sprint 3 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C06 | Questions and ReviewLens responses are persisted | Saved analysis retains meaningful Q&A records associated with that AnalysisTarget | S3-006 |  |
| C07 | Q&A history is restored with the correct analysis | Reopening/switching analyses loads only the history belonging to the active analysis | S3-007 |  |
| C08 | Q&A history can be cleared without deleting analysis data | Clearing history leaves the AnalysisTarget, review dataset, source, and ingestion summary intact | S3-008 |  |

### C. Review Refresh and Re-Ingestion

| ID | Criterion | Evidence to Observe | Sprint 3 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C09 | Existing analysis can be refreshed/re-ingested | User can initiate a new ingestion attempt without creating a new AnalysisTarget | S3-009 |  |
| C10 | Successful refresh becomes the current dataset coherently | Summary, review browsing, Q&A, and export all reflect the newly current dataset | S3-010 |  |
| C11 | Re-ingestion prevents duplicate source reviews | Team demonstrates or directly evidences a deterministic duplicate strategy and automated test coverage | S3-011 |  |
| C12 | Failed refresh preserves the last known-good dataset | Failure is recorded/communicated without replacing valid persisted review data | S3-012 |  |

### D. Evidence and Review Exploration

| ID | Criterion | Evidence to Observe | Sprint 3 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C13 | Grounded answers display supporting review evidence | Representative persisted reviews are shown with the answer and correspond to the active AnalysisTarget | S3-013 |  |
| C14 | User can inspect matching/supporting reviews | Application provides access to the broader set of reviews identified as relevant to the grounded answer when such a set exists | S3-014 |  |
| C15 | User can browse the complete current review dataset | Complete active dataset is inspectable with useful review fields rather than only a small preview | S3-015 |  |
| C16 | User can filter reviews by rating and date | Filters operate correctly on the active persisted dataset; date filtering is demonstrated when source dates exist | S3-016 |  |

### E. Export

| ID | Criterion | Evidence to Observe | Sprint 3 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C17 | Active review dataset exports correctly to CSV | Download contains representative current persisted review data and respects ownership boundaries | S3-017 |  |
| C18 | Saved analysis exports correctly to Markdown | Download contains useful analysis context, summary, Q&A history when present, and supporting evidence when applicable | S3-018 |  |
| C19 | Export filenames and metadata are meaningful | Files are named from the analysis/entity rather than generically and include useful identifying metadata where appropriate | S3-019 |  |

### F. Public Delivery

| ID | Criterion | Evidence to Observe | Sprint 3 Story Coverage | Score |
| --- | --- | --- | --- | --- |
| C20 | Complete ReviewLens application is publicly deployed | Stable public URL supports authentication, ownership isolation, saved analyses, ingestion/refresh, summary, review exploration, grounded Q&A, scope guards, Q&A history, and export | S3-020 |  |
