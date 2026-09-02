# Sprint 2 Demo Script (Fall 2026)

_ReviewLens AI - CS 490 Capstone_

## 1. Purpose

This document defines exactly how teams should prepare for and run the Sprint 2 ReviewLens AI demonstration.

Sprint 2 should demonstrate that ReviewLens has progressed from collecting review data to providing trustworthy review intelligence.

The demo should show:

1. A clear ingestion result summary derived from persisted review data.
2. Review-grounded natural-language Q&A.
3. Correct handling of questions that cannot be answered from the available reviews.
4. Scope guards that reject unrelated questions.
5. Correct switching between AnalysisTargets without stale context.
6. Protection against cross-user review data entering AI context.
7. Stronger integration, coverage, and AI-behavior testing.
8. Continued continuous-integration enforcement.

The demo should be presented as one coherent ReviewLens workflow rather than as a sequence of Jira tickets.

The instructor may ask technical questions at any point during the demonstration. Questions are part of the demo and do not stop the clock.

---

## 2. Hard Time Limit

The Sprint 2 demo has a **20-minute hard cap**.

The clock includes:

1. Application startup or loading.
2. Instructor questions.
3. Switching AnalysisTargets.
4. Waiting for model responses.
5. Opening tests or CI evidence.
6. Recovery from application or environment problems.
7. Any other setup performed after the demo begins.

**The demo ends at 20 minutes whether or not every required item has been shown.**

Any required behavior not demonstrated before time expires is considered not demonstrated.

Teams are expected to rehearse the complete demo and prepare all required data, prompts, questions, tests, browser tabs, terminals, and CI evidence before class.

A prepared team should be able to complete the planned demonstration in approximately **16-17 minutes**, leaving room for instructor questions.

---

## 3. Required Demo Preparation

Sprint 2 depends heavily on the quality of the prepared review datasets and questions. Teams should not improvise these during the demo.

Everything needed for the demonstration should be prepared before the team is called.

### 3.1 Required User Accounts and AnalysisTargets

Prepare **two working registered accounts**.

#### User A — Primary Demo Account

User A should have at least **two AnalysisTargets**, both containing successfully ingested review data.

Prepare the two datasets so they are clearly distinguishable.

For example:

- **Target A** might contain reviews where "battery life" is a recurring theme.
- **Target B** might contain reviews where "customer service" is a recurring theme.

The exact subject matter is the team's choice, but the datasets should contain visibly different evidence so that a change in Q&A context can be demonstrated clearly.

Each primary dataset should contain enough meaningful review data to support analysis. As a guideline, prepare approximately **20 or more real reviews per target**.

#### User B — Security / Isolation Account

User B should have at least:

1. One AnalysisTarget.
2. A real persisted review dataset.
3. Review content that is clearly distinguishable from User A's data.

For testing cross-user AI isolation, it is useful to include a distinctive phrase or fact in User B's test dataset that does not appear in User A's data.

### 3.2 Required Ingestion Summary Data

At least one prepared AnalysisTarget must include data sufficient to demonstrate:

1. Successful ingestion status.
2. Number of successfully ingested reviews.
3. Basic rating information.
4. Skipped or rejected records, if the team's ingestion process supports or encounters them.
5. Clear identification of the AnalysisTarget represented by the summary.

The team should know the expected summary values before the demo begins.

Do not use an ingestion summary whose correctness cannot be verified.

### 3.3 Required Q&A Questions

Prepare the exact questions that will be used during the demo.

At minimum, prepare:

1. **One clearly in-scope question** that the active review dataset can answer.
2. **One in-scope question with insufficient evidence** in the active dataset.
3. **One unrelated general-knowledge question** that ReviewLens must decline.
4. **One question about another product, entity, or review platform** that ReviewLens must decline.
5. **One question for Target A** whose answer depends on Target A's distinctive review content.
6. **One question for Target B** whose answer depends on Target B's distinctive review content.

These questions should be tested before demo day.

The team should not spend demo time inventing prompts or experimenting to find one that produces the desired behavior.

### 3.4 Required Testing and CI Evidence

Before the demo begins, identify and be ready to show:

1. The changed-code coverage gate.
2. At least one critical integration test.
3. The deterministic Q&A test harness.
4. The scope-guard evaluation set.
5. A test proving that the active AnalysisTarget determines the Q&A context.
6. A test proving that cross-user review data does not enter AI context.
7. A recent successful CI workflow showing the Sprint 2 quality gates.

The team should be prepared to explain how deterministic CI testing is separated from nondeterministic live-model behavior.

### 3.5 Team Environment Readiness

For Sprint 2, **the instructor will randomly select one team member's development computer as the demonstration device**.

Every team member must therefore have a working development environment capable of:

1. Pulling the current codebase.
2. Installing required dependencies.
3. Running the application.
4. Running the automated tests.
5. Accessing required development services.
6. Using the documented environment configuration.
7. Accessing the team's selected LLM and other required external services.

The team may not assume that the developer with the best-configured laptop will run the demo.

The project should not depend on a single "magic laptop."

Time spent correcting the randomly selected environment counts against the 20-minute hard cap.

### 3.6 Demo Readiness and Rehearsal

The team should arrive knowing:

1. Which two User A AnalysisTargets will be demonstrated.
2. What evidence makes the two datasets clearly distinguishable.
3. The expected ingestion summary values.
4. The exact in-scope and out-of-scope questions that will be asked.
5. Which question demonstrates insufficient evidence.
6. Which question demonstrates target switching.
7. Which tests will be shown.
8. Which CI workflow will be shown.
9. Which team member will explain each major area.

Avoidable preparation problems are not reasons to extend the demo.

---

## 4. Before the Clock Starts

Before the team is called:

1. Confirm that every team member can run the application.
2. Confirm that both User A AnalysisTargets contain the expected review data.
3. Confirm that User B's distinct dataset exists.
4. Confirm that the ingestion summary values are known.
5. Confirm that the prepared Q&A questions behave as expected.
6. Confirm that the live model service is reachable.
7. Confirm that required tests pass.
8. Confirm that the CI evidence is available.
9. Open any browser tabs, terminals, test files, or CI pages that will be needed.

When called, the instructor will select the development computer used for the demo.

Do not begin with a slide deck or project-history presentation.

Start with the working application.

---

## 5. Live Demo Script

The sequence below is the expected Sprint 2 demonstration order.

### Step 1 — Open the Active AnalysisTarget and Establish Context

**Target time: approximately 1 minute**

Authenticate as **User A** and open the first prepared AnalysisTarget.

Show that the active workspace clearly identifies:

1. Target/entity name.
2. Review platform.
3. Source or source reference.
4. Current ingestion state.
5. The review dataset that will be analyzed.

Briefly identify the distinctive theme or evidence intentionally present in this dataset.

Do not repeat the full Sprint 1 authentication or target-creation demonstration.

### Step 2 — Demonstrate the Ingestion Result Summary

**Target time: approximately 2-3 minutes**

Show the ingestion summary for the active AnalysisTarget.

Demonstrate:

1. Ingestion result status.
2. Number of successfully ingested reviews.
3. Basic rating information.
4. Skipped or rejected record information when applicable.
5. Clear identification of which AnalysisTarget the summary represents.

Then show enough persisted review data to verify that the summary is plausible.

The summary must be derived from application data, not generated speculatively by the LLM.

Be prepared to explain where the summary calculation occurs and why the Q&A workflow is using the same active dataset.

### Step 3 — Ask a Grounded In-Scope Question

**Target time: approximately 2 minutes**

Submit the prepared in-scope question that the active review dataset can answer.

Show that ReviewLens:

1. Accepts the question.
2. Uses the active AnalysisTarget's review data.
3. Produces a useful answer connected to evidence in the reviews.
4. Does not introduce unrelated information.

The team should be able to point to representative review evidence that supports the answer.

Be prepared to explain:

1. How review context is selected.
2. How the context is passed to the model.
3. What happens if the dataset is too large to send to the model directly.
4. Why the team chose its current retrieval/context strategy.

### Step 4 — Demonstrate Insufficient Evidence Handling

**Target time: approximately 1-2 minutes**

Ask the prepared question that is relevant to the target but cannot be answered from the available reviews.

Show that ReviewLens:

1. Recognizes that the question is conceptually related to the active target.
2. Does not invent unsupported information.
3. Clearly communicates that the available review data does not provide enough evidence.

### Step 5 — Demonstrate the Scope Guard

**Target time: approximately 2-3 minutes**

Ask the prepared **general-knowledge question**.

Show that ReviewLens declines the question and explains that it is limited to the active review dataset.

Then ask the prepared question about another product, entity, or review platform.

Show that ReviewLens declines that question as well.

The team should be prepared to show or explain the system prompt that defines these boundaries.

The scope guard should arise primarily from:

1. The system prompt.
2. The active application context.

It should not be implemented as a hard-coded blacklist containing only the exact demo questions.

### Step 6 — Switch AnalysisTargets and Prove Context Changed

**Target time: approximately 2-3 minutes**

Switch from **Target A** to **Target B**.

Show that the application now clearly identifies Target B as active.

Then ask the prepared Target B question.

The answer should demonstrate that ReviewLens is using Target B's distinctive review data.

After switching to Target B:

1. Target B review content should enter the AI context.
2. Target A review content should no longer be supplied.
3. The ingestion summary should correspond to Target B.
4. The UI should identify Target B as active.

Be prepared to explain how the implementation prevents stale context when changing targets.

### Step 7 — Show Cross-User AI Context Isolation Evidence

**Target time: approximately 1-2 minutes**

Sprint 1 already required a live cross-user authorization attack.

For Sprint 2, focus on the new security boundary: **what data enters the AI context**.

Show an automated test or controlled test-harness scenario using at least two users.

The evidence should demonstrate that:

1. User A's Q&A request loads only User A's active target reviews.
2. User B's distinctive review content is not included in User A's model context.
3. The model boundary can be inspected or captured sufficiently to verify which review data was supplied.

Where practical, show the mocked or controlled LLM request/context rather than judging isolation only from generated prose.

### Step 8 — Show the Sprint 2 Quality-Assurance Ratchet

**Target time: approximately 2-3 minutes**

Show representative Sprint 2 test and CI evidence.

Demonstrate:

1. **Changed-code coverage gate**
2. **Critical integration testing**
3. **Deterministic Q&A test harness**
4. **Scope-guard evaluation set**
5. **CI enforcement**

Do not spend demo time scrolling through large test suites or coverage reports.

Show representative evidence and explain what each mechanism protects against.

### Step 9 — Close the Demo

**Target time: approximately 30 seconds**

Conclude with two brief statements:

1. What ReviewLens can now do that it could not do at the end of Sprint 1.
2. What the team considers its largest technical or operational risk entering Sprint 3.

---

## 6. Instructor Questions During the Demo

The instructor may ask questions at any point.

Questions may address:

1. Ingestion-summary calculations.
2. Review-context selection.
3. Prompt design.
4. Scope enforcement.
5. LLM failure behavior.
6. Target switching.
7. Cross-user AI context isolation.
8. Deterministic AI testing.
9. Integration testing.
10. Changed-code coverage.
11. Architecture and design tradeoffs.
12. Code written or modified by a specific team member.

The team member responsible for the relevant area should normally answer.

The instructor may ask to see code, prompts, tests, model-context construction, persistence behavior, or CI configuration when needed to clarify what is being demonstrated.

**The demo clock continues while questions are being answered.**

---

## 7. Final Preparation Checklist

Before demo day, confirm all of the following:

- [ ] Every team member can build, test, and run the application.
- [ ] User A account works.
- [ ] User B account works.
- [ ] User A has at least two populated AnalysisTargets.
- [ ] Both User A datasets contain meaningful real review data.
- [ ] The two User A datasets have clearly distinguishable themes/evidence.
- [ ] User B has a distinct persisted dataset.
- [ ] Expected ingestion-summary values are known.
- [ ] In-scope grounded question is prepared.
- [ ] Insufficient-evidence question is prepared.
- [ ] General-knowledge scope-guard question is prepared.
- [ ] Other-entity/platform scope-guard question is prepared.
- [ ] Target A context question is prepared.
- [ ] Target B context question is prepared.
- [ ] Changed-code coverage evidence is identified.
- [ ] Critical integration test is identified.
- [ ] Deterministic Q&A test-harness evidence is identified.
- [ ] Scope-guard evaluation set is ready.
- [ ] Cross-user AI-context isolation test is ready.
- [ ] Latest relevant CI workflow is easy to access.
- [ ] Required environment configuration works on every team member's device.
- [ ] Demo browser tabs/tools are prepared.
- [ ] Team members know who will explain each area.
- [ ] The complete demonstration has been rehearsed within the 20-minute hard cap.
