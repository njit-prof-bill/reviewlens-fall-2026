# ReviewLens AI - Sprint 2 Stories (Fall 2026)

This is the Sprint 2 backlog for the ReviewLens AI capstone project.

Story writing format for Jira:

- Story ID
- Title
- Outcome — what must be true when complete
- Technical Guidance — implementation boundaries and expectations
- Rules — applicable canonical business rules

Sprint 2 focus: Ingestion intelligence, review-grounded Q&A, scope guard enforcement, analysis context management, and a stronger quality-assurance baseline.

Total stories: 20

Stories S2-001 through S2-004 establish the Sprint 2 quality-assurance ratchet and are primarily team-level engineering work.

Stories S2-005 through S2-020 define the primary application capabilities for Sprint 2. These 16 feature stories provide approximately three to four primary feature stories per developer for a five-person team.

## How To Read This Sprint Document

1. This file is the authoritative source for Sprint 2 scope.
2. `README.md` provides the overall product description, but Sprint 2 grading is based on this file.
3. Sprint 1 requirements remain in force unless explicitly changed here.
4. Features described in the overall product but not listed here are not required for Sprint 2.
5. Technical Guidance defines important implementation expectations but intentionally does not prescribe a specific application architecture, LLM provider, retrieval strategy, database, framework, or cloud platform unless explicitly stated.
6. Teams should make reasonable engineering decisions where implementation details are unspecified.
7. Features planned for Sprint 3 should not be implemented early unless explicitly approved.

## Sprint 2 Demonstration Goal

The Sprint 2 application should demonstrate the following end-to-end workflow:

1. A user authenticates and opens an AnalysisTarget containing ingested reviews.
2. The user sees a trustworthy summary of the active review dataset.
3. The user asks a question that can be answered from those reviews.
4. ReviewLens provides an answer grounded in the active dataset.
5. The user asks a relevant question that cannot be supported by the available reviews.
6. ReviewLens explains that the available data is insufficient rather than inventing an answer.
7. The user asks an unrelated or out-of-scope question.
8. ReviewLens explicitly declines the question.
9. The user switches to another AnalysisTarget.
10. Subsequent Q&A uses only the newly selected target's reviews.
11. Cross-user data remains isolated throughout the Q&A process.

The team should demonstrate these behaviors as a coherent ReviewLens workflow rather than presenting each Jira story independently.

---

# CI/CD and Testing Requirements (Required)

Sprint 1 CI/CD and testing requirements remain mandatory.

Sprint 2 adds stronger integration, coverage, and AI-behavior testing requirements.

## CI/CD Sprint 2 Ratchet

Every pull request must continue to run:

1. Lint or equivalent static checks.
2. Application build.
3. Automated unit tests.

Sprint 2 additionally requires:

4. Required integration tests.
5. A changed-code coverage gate or equivalent mechanism that prevents newly changed code from bypassing meaningful automated test coverage.
6. Required AI orchestration and scope-guard tests.
7. A pull request with any required failing check cannot be merged through the team's normal protected-branch workflow.
8. CI output must remain visible to reviewers before merge.

## Test Baseline Expectations

1. Every feature story must include an appropriate automated test update.
2. Tests should verify observable behavior rather than internal implementation details whenever practical.
3. Sprint 1 authentication, authorization, ownership, and validation tests must continue to pass.
4. Integration tests must cover important service and persistence boundaries.
5. AI-related behavior must be tested at the application orchestration layer.
6. Automated CI tests should not depend on a live LLM returning an exact natural-language sentence.
7. External LLM responses should be mocked, stubbed, recorded, or otherwise controlled where deterministic CI behavior is required.
8. The team must also maintain a representative AI evaluation set containing both:
   - in-scope questions that ReviewLens should answer
   - out-of-scope questions that ReviewLens should decline
9. Tests should evaluate required behavior rather than exact wording where natural-language variation is reasonable.
10. Cross-user Q&A tests must prove that another user's review content cannot enter the active AI context.

## Minimum Test Evidence by Story Type

### Ingestion Summary

1. Summary values match known persisted review fixtures.
2. Success and failure states are represented correctly.
3. Invalid or skipped data is represented consistently when applicable.

### Review Q&A

1. An in-scope question reaches the Q&A orchestration path.
2. The active AnalysisTarget determines the review context.
3. Review data supplied to the AI belongs to the active target.
4. An expected answer can be produced from controlled test context.
5. Insufficient evidence results in the expected application behavior.

### Scope Guard

1. Representative in-scope questions are accepted.
2. Representative general-knowledge questions are declined.
3. Representative questions about another product, entity, or platform are declined.
4. Tests do not require one exact refusal sentence.

### Context and Ownership

1. Changing AnalysisTarget changes review context.
2. Previous target data is not retained accidentally.
3. Cross-user review data is excluded from AI context.
4. Attempts to select another user's target remain denied.

## Definition of Done Additions

A Sprint 2 story is not complete until:

1. The story outcome works in the running application.
2. Required automated tests pass locally.
3. Required automated tests pass in CI.
4. Sprint 1 regression tests continue to pass.
5. Changed-code coverage requirements pass.
6. The story does not knowingly weaken authentication, authorization, ownership, or ingestion behavior established in Sprint 1.
7. The pull request contains a short `Test Evidence` section describing the tests used to verify the story.
8. AI-related stories document important prompt, context, or model assumptions where another developer would reasonably need to understand them.

---

# Canonical Business Rules (Sprint 2)

These rules are authoritative for Sprint 2 implementation and grading.

## S2-BR Ingestion Result Summary

1. **S2-BR-001**: The application must clearly identify the AnalysisTarget represented by an ingestion summary.
2. **S2-BR-002**: Summary values must be computed from application data and must not be fabricated by an LLM.
3. **S2-BR-003**: The summary must show the number of successfully ingested reviews.
4. **S2-BR-004**: The summary must provide basic rating information derived from the ingested review data.
5. **S2-BR-005**: The user must be able to distinguish successful, failed, and partial ingestion when the implementation supports partial success.
6. **S2-BR-006**: Rejected, skipped, or unprocessable records must not silently appear as successfully ingested reviews.
7. **S2-BR-007**: The ingestion summary must represent the dataset that will be used by the Q&A workflow.

## S2-BR Review-Grounded Q&A

1. **S2-BR-008**: ReviewLens must provide a user-facing interface for asking natural-language questions about the active AnalysisTarget.
2. **S2-BR-009**: Q&A responses must be based on reviews belonging to the active AnalysisTarget.
3. **S2-BR-010**: ReviewLens must not claim review evidence that is not contained in the active dataset.
4. **S2-BR-011**: If the available reviews do not provide sufficient evidence for an answer, ReviewLens must communicate that limitation rather than inventing information.
5. **S2-BR-012**: The method used to provide review context to the LLM is an architectural decision for the team.
6. **S2-BR-013**: A vector database, embeddings, or a particular RAG architecture is not required merely because the application contains AI functionality.
7. **S2-BR-014**: The Q&A workflow must remain associated with the authenticated user's selected AnalysisTarget.

## S2-BR Scope Guard

1. **S2-BR-015**: The system prompt must explicitly define ReviewLens as answering questions only from the active review dataset.
2. **S2-BR-016**: General world-knowledge questions unrelated to the active reviews must be declined.
3. **S2-BR-017**: Questions about another product, business, location, or entity not represented by the active dataset must be declined.
4. **S2-BR-018**: Questions about another review platform must be declined when that platform's data is not contained in the active dataset.
5. **S2-BR-019**: Scope enforcement must be driven primarily by the system prompt and supplied application context.
6. **S2-BR-020**: Supporting application logic may reinforce the scope guard but must not replace a clear prompt-level scope definition.
7. **S2-BR-021**: A refusal should be clear and useful to the user without pretending the requested information was analyzed.

## S2-BR Context and User Isolation

1. **S2-BR-022**: Only review data belonging to the authenticated user may enter that user's AI context.
2. **S2-BR-023**: Changing the active AnalysisTarget must change the review dataset used for subsequent Q&A.
3. **S2-BR-024**: Review data from a previously selected target must not remain in the active context after the target changes.
4. **S2-BR-025**: A target with no successfully ingested review data cannot provide a normal review-grounded answer.
5. **S2-BR-026**: Existing Sprint 1 backend ownership rules remain authoritative for all Sprint 2 Q&A and summary operations.

## S2-BR AI Testing

1. **S2-BR-027**: The team must maintain automated tests for the Q&A orchestration layer.
2. **S2-BR-028**: The team must maintain a representative scope-guard evaluation set containing both accepted and rejected question types.
3. **S2-BR-029**: CI tests must not depend on an exact natural-language response from a nondeterministic live model.
4. **S2-BR-030**: Tests must verify behavioral properties such as accepted scope, rejected scope, correct dataset selection, and absence of cross-user context.
5. **S2-BR-031**: Live-model testing may supplement deterministic automated tests but does not replace them.

## Rule Usage in Stories and Jira

1. Any Sprint 2 story may reference one or more S2-BR IDs instead of repeating the complete rule text.
2. Sprint 1 canonical business rules remain applicable where relevant.
3. If story behavior conflicts with a canonical business rule, the canonical business rule prevails.
4. A developer implementing a story is responsible for understanding all rules referenced by that story.

---

# A. Sprint 2 Quality-Assurance Ratchet

These are primarily team-level engineering stories.

## S2-001 - Add Changed-Code Coverage Gate

**Outcome:**  
The CI pipeline measures automated test coverage for changed or newly added code and rejects a pull request that fails the team's required threshold.

**Technical Guidance:**

The team may select an appropriate coverage tool and threshold for its technology stack.

The objective is not to maximize a vanity percentage. The objective is to prevent significant new behavior from entering the codebase without automated verification.

The team should document:

1. The selected coverage mechanism.
2. The required threshold or policy.
3. Which code is excluded and why, if exclusions exist.
4. How a developer can run the coverage check locally.

A deliberately under-tested change should be capable of causing the gate to fail.

**Rules:** S2-BR-027 through S2-BR-031

## S2-002 - Add Critical Integration Test Coverage

**Outcome:**  
The project contains automated integration tests covering important Sprint 2 boundaries between application services, persistence, ingestion data, and Q&A orchestration.

**Technical Guidance:**

Integration tests should focus on boundaries where independently correct components could still fail when combined.

Representative areas include:

1. Loading persisted reviews for an AnalysisTarget.
2. Computing an ingestion summary from persisted data.
3. Passing the correct review dataset into the Q&A service.
4. Applying authenticated ownership before review retrieval.
5. Changing the active target and retrieving different data.

The exact testing technology is the team's decision.

**Rules:** S2-BR-001 through S2-BR-014, S2-BR-022 through S2-BR-030

## S2-003 - Create Deterministic Q&A Test Harness

**Outcome:**  
The team can automatically test ReviewLens Q&A orchestration without depending on unpredictable live-model output.

**Technical Guidance:**

The test harness should make it possible to verify what the application sends to and receives from the model boundary.

Possible approaches include:

1. Mock LLM client.
2. Stubbed model adapter.
3. Recorded model responses.
4. Dependency injection around the AI provider.
5. Equivalent controlled testing approach.

Tests should be able to verify:

1. Correct system instructions are supplied.
2. Correct review context is supplied.
3. Wrong-target reviews are not supplied.
4. Cross-user reviews are not supplied.
5. Application behavior is correct for controlled model responses.

The test architecture should not require developers to spend money on model API calls every time CI runs.

**Rules:** S2-BR-009 through S2-BR-014, S2-BR-022, S2-BR-027 through S2-BR-031

## S2-004 - Create Scope-Guard Evaluation Set

**Outcome:**  
The team maintains a repeatable set of representative questions used to verify ReviewLens scope behavior.

**Technical Guidance:**

The evaluation set must include multiple examples from at least these categories:

1. Clearly in-scope review questions.
2. Relevant questions for which the dataset lacks sufficient evidence.
3. General world-knowledge questions.
4. Questions about another product or entity.
5. Questions about another review platform.

The evaluation should determine whether the behavior is acceptable without requiring one exact answer sentence.

The team may implement the evaluation as automated tests, structured fixtures, an evaluation script, or a combination.

A small, thoughtful evaluation set is preferable to a large set of redundant examples.

**Rules:** S2-BR-015 through S2-BR-021, S2-BR-027 through S2-BR-031

---

# B. Ingestion Result Summary

## S2-005 - Display Ingestion Result Status

**Outcome:**  
The AnalysisTarget workspace clearly communicates the result state of the ingestion operation associated with the active dataset.

**Technical Guidance:**

The user must be able to distinguish at least:

1. Successful ingestion.
2. Failed ingestion.

If the team's Sprint 1 implementation supports partial success, the UI should represent that state distinctly.

If ingestion is asynchronous, a processing state should also be represented.

The displayed result should come from persisted ingestion state rather than being inferred solely from the presence of review rows.

**Rules:** S2-BR-001, S2-BR-005 through S2-BR-007

## S2-006 - Display Review Count and Rating Summary

**Outcome:**  
The user can see the number of successfully ingested reviews and basic rating information for the active AnalysisTarget.

**Technical Guidance:**

At minimum, display:

1. Number of successfully ingested reviews.
2. Basic rating information appropriate to the selected review platform.

Examples of appropriate rating information include:

1. Average rating.
2. Rating distribution.
3. Counts by rating value.

The team does not need to implement every possible metric.

All displayed values must be calculated from persisted review data.

Tests should use a known review fixture so expected values can be asserted exactly.

**Rules:** S2-BR-001 through S2-BR-004, S2-BR-007

## S2-007 - Report Skipped or Rejected Review Records

**Outcome:**  
When ingestion encounters individual records that cannot be processed, the user can determine that those records were not included in the active review dataset.

**Technical Guidance:**

The application does not need to expose raw parser diagnostics to the user.

A reasonable summary may communicate:

1. Number successfully ingested.
2. Number skipped or rejected.
3. A concise reason category when useful.

For example:

- missing review text
- invalid rating
- malformed source record

The exact level of detail is a team design decision.

The important requirement is that unsuccessful records do not silently count as successfully analyzed data.

**Rules:** S2-BR-005 through S2-BR-007

## S2-008 - Derive Summary from the Active Persisted Dataset

**Outcome:**  
The ingestion summary accurately represents the same persisted review dataset that will be used by Q&A.

**Technical Guidance:**

The summary should not be separately generated from stale source data, browser-only state, or LLM interpretation.

Tests should demonstrate that:

1. Adding or removing a persisted test Review changes the calculated summary appropriately.
2. Target A summary uses Target A reviews.
3. Target B summary uses Target B reviews.
4. User A cannot retrieve User B's summary.

This story establishes a common data boundary between ingestion and analysis.

**Rules:** S2-BR-001 through S2-BR-007, S2-BR-022, S2-BR-026

---

# C. Review-Grounded Q&A

## S2-009 - Build the Review Q&A Interface

**Outcome:**  
A user can submit a natural-language question from the active AnalysisTarget workspace and receive a ReviewLens response.

**Technical Guidance:**

At minimum, the interface should include:

1. Question input.
2. Submit action.
3. Processing/loading state.
4. Response display.
5. Meaningful error state if the AI request fails.

A full persistent chat-history system is not required.

A simple question-and-response interaction is acceptable if it supports the required analysis workflow.

The active AnalysisTarget must remain clear while the user asks questions.

**Rules:** S2-BR-008, S2-BR-014

## S2-010 - Build Review Dataset Context for Q&A

**Outcome:**  
Before a question is submitted to the LLM, ReviewLens constructs AI context from reviews belonging to the active AnalysisTarget.

**Technical Guidance:**

The team must make an explicit architectural decision for selecting and supplying review context.

Possible approaches include:

1. Supplying all reviews when the dataset is small enough.
2. Selecting relevant reviews before model invocation.
3. Retrieval-Augmented Generation.
4. Embeddings and vector search.
5. Search or filtering strategies.
6. Another defensible approach appropriate to the team's dataset size.

No particular retrieval architecture is required.

The implementation must ensure:

1. Context comes from persisted ReviewLens data.
2. Context belongs to the active AnalysisTarget.
3. Context belongs to the authenticated user.
4. Context does not accidentally include a previously selected target.

The team should document important context-size or model-token limitations.

**Rules:** S2-BR-009, S2-BR-012 through S2-BR-014, S2-BR-022 through S2-BR-026

## S2-011 - Answer Questions from Review Evidence

**Outcome:**  
For an in-scope question supported by the active review dataset, ReviewLens produces a useful answer based on those reviews.

**Technical Guidance:**

Representative questions might include:

- What complaints appear most frequently?
- What do customers like about this product?
- Are there recurring complaints about customer service?
- What themes appear in low-rated reviews?
- What reasons do reviewers give for high ratings?

The exact wording and presentation of answers are team design decisions.

The team should design the system prompt and review context so that the model treats supplied reviews as its evidence base.

The application is not expected to produce mathematically perfect natural-language analysis, but answers should be defensibly connected to the review content.

**Rules:** S2-BR-008 through S2-BR-014

## S2-012 - Handle Questions with Insufficient Review Evidence

**Outcome:**  
When a question is within the general review-analysis domain but the active dataset does not contain sufficient information to answer it, ReviewLens communicates that limitation.

**Technical Guidance:**

Example:

The reviews discuss food quality and service, but the user asks:

> "Do customers think the parking lot is safe at night?"

If the reviews provide no evidence about parking safety, ReviewLens should not infer an answer from general knowledge.

The system prompt should explicitly instruct the model to distinguish:

1. Information supported by the reviews.
2. Information absent from the reviews.

Tests should include a controlled dataset where the absence of evidence is known.

**Rules:** S2-BR-010, S2-BR-011, S2-BR-015

---

# D. Q&A Scope Guard

## S2-013 - Define and Apply the ReviewLens System Prompt

**Outcome:**  
Every ReviewLens Q&A request uses a system prompt that explicitly constrains the assistant to the active review dataset.

**Technical Guidance:**

The system prompt should communicate at least:

1. Which product/entity is currently being analyzed.
2. Which review platform supplied the data.
3. That answers must be based on the supplied review dataset.
4. That unsupported information must not be invented.
5. That unrelated general-knowledge questions must be declined.
6. That questions about another product, entity, or unsupported platform must be declined.

The prompt may contain additional instructions selected by the team.

Prompt text should be maintained in source control or another reviewable configuration location.

It should not exist only as an undocumented string entered manually in a hosted AI console.

**Rules:** S2-BR-015 through S2-BR-021

## S2-014 - Reject General-Knowledge Questions

**Outcome:**  
ReviewLens gracefully declines questions that are unrelated to the active review dataset.

**Technical Guidance:**

Representative examples include:

- What is the weather today?
- Who is the President of the United States?
- Write a Python sorting algorithm.
- What are the best restaurants in New York?

The refusal should make the ReviewLens scope clear and may invite the user to ask a question about the active reviews.

The team should not implement these examples as a hard-coded blacklist.

The behavior should arise primarily from the system prompt and application context.

**Rules:** S2-BR-015, S2-BR-016, S2-BR-019 through S2-BR-021

## S2-015 - Reject Questions About Another Entity or Platform

**Outcome:**  
ReviewLens declines questions that request analysis of a product, entity, or review platform not represented in the active dataset.

**Technical Guidance:**

For example, if the active target represents Google Maps reviews for Restaurant A, ReviewLens should not answer:

- What do customers think about Restaurant B?
- What are Restaurant A's Yelp reviews like?
- How does Restaurant A compare with Restaurant B based on Amazon reviews?

A comparison may be answered only when the required evidence actually exists within the active ReviewLens dataset.

Tests should include both obvious and reasonably phrased out-of-scope examples.

**Rules:** S2-BR-017 through S2-BR-021

## S2-016 - Prevent Cross-User Data from Entering AI Context

**Outcome:**  
The Q&A orchestration layer cannot supply another authenticated user's review data to the LLM.

**Technical Guidance:**

This is a backend security requirement, not merely a UI requirement.

Automated tests should use at least two users and two datasets.

For example:

1. User A owns Target A containing a distinctive review phrase.
2. User B owns Target B.
3. User B asks a question designed to expose the distinctive Target A content.
4. Target A reviews are not included in User B's AI context.
5. The response does not obtain Target A information through the application's Q&A pipeline.

Where practical, tests should inspect or capture the context passed to the mocked LLM boundary rather than judging security only from generated prose.

**Rules:** S2-BR-022, S2-BR-026 through S2-BR-030

---

# E. Analysis Context Management

## S2-017 - Switch the Active AnalysisTarget

**Outcome:**  
A user can move from one owned AnalysisTarget to another and clearly see which target is currently active.

**Technical Guidance:**

The active target should be represented consistently across:

1. Target workspace.
2. Ingestion summary.
3. Q&A interface.

A user should not have to infer which review dataset is being analyzed.

Direct selection of another user's target remains prohibited by Sprint 1 authorization rules.

**Rules:** S2-BR-001, S2-BR-014, S2-BR-022 through S2-BR-026

## S2-018 - Change Q&A Context When the Target Changes

**Outcome:**  
After the user switches AnalysisTargets, subsequent Q&A uses the newly selected target's reviews.

**Technical Guidance:**

Automated tests should create clearly distinguishable datasets.

For example:

- Target A reviews repeatedly mention "battery life."
- Target B reviews repeatedly mention "customer service."

After switching from Target A to Target B:

1. New AI context should contain Target B review data.
2. Target A review data should no longer be supplied.
3. Summary information should correspond to Target B.
4. The UI should clearly identify Target B as active.

**Rules:** S2-BR-023, S2-BR-024

## S2-019 - Prevent Stale Review Context

**Outcome:**  
ReviewLens does not accidentally retain reviews from a previously active AnalysisTarget when processing a new question.

**Technical Guidance:**

This requirement applies regardless of whether the team stores Q&A state:

1. In frontend state.
2. In backend session state.
3. In a database.
4. In a retrieval index.
5. Through an external AI service.

The team should explicitly test the transition between targets rather than testing each target only in isolation.

If the implementation caches review context, cache keys and invalidation must preserve target and user boundaries.

**Rules:** S2-BR-022 through S2-BR-024

## S2-020 - Handle a Target Without Review Data

**Outcome:**  
When an AnalysisTarget has no successfully ingested review dataset, ReviewLens does not present normal review-grounded Q&A as though data were available.

**Technical Guidance:**

The application should provide a clear state such as:

- No reviews have been ingested.
- The most recent ingestion failed.
- Complete ingestion before asking ReviewLens questions.

The exact UX is a team decision.

The important requirement is that the LLM must not substitute general knowledge because ReviewLens has no review context.

Tests should verify that an empty target does not result in a normal grounded-answer workflow.

**Rules:** S2-BR-007, S2-BR-010, S2-BR-011, S2-BR-025

---

# Sprint 2 Demo Expectations

The team has approximately 15 minutes to demonstrate the Sprint 2 increment.

The demo should emphasize the complete review-intelligence workflow and evidence that the AI behavior is tested rather than simply showing a chatbot.

A recommended demonstration flow is:

1. Briefly show that Sprint 2 CI includes the new integration, coverage, and AI-behavior gates.
2. Authenticate and open an AnalysisTarget containing review data.
3. Show the ingestion result summary.
4. Demonstrate that summary counts or ratings correspond to actual persisted review data.
5. Ask a clearly in-scope review question.
6. Show ReviewLens answering from the active reviews.
7. Ask a relevant question for which the reviews do not contain enough evidence.
8. Show ReviewLens acknowledge the limitation.
9. Ask a clearly unrelated general-knowledge question.
10. Show the scope guard decline it.
11. Ask about another product, entity, or review platform.
12. Show that request declined.
13. Switch to a second AnalysisTarget.
14. Ask a question whose answer demonstrates that the Q&A context changed.
15. Briefly show representative automated tests, including a scope-guard test and a cross-user context test.

The team does not need to demonstrate every individual Jira story or every evaluation case.

Every team member should be prepared to explain:

1. The stories they implemented.
2. The automated tests supporting those stories.
3. How their changes passed through CI.
4. How deterministic AI testing was separated from nondeterministic live-model behavior.
5. Important implementation decisions or tradeoffs.

---

# Sprint 2 Explicitly Out of Scope

The following functionality is not required for Sprint 2:

1. Multiple supported review platforms.
2. General-purpose AI chat.
3. Persistent multi-session chat history.
4. Complex conversational memory.
5. A specific vector database or embedding technology.
6. A specific RAG framework.
7. Fine-tuning an LLM.
8. Training a custom machine-learning model.
9. Sentiment analysis beyond what the team chooses to expose through review Q&A.
10. Advanced dashboards or business-intelligence reporting.
11. Production deployment.
12. Automated production deployment.
13. Post-deployment health checks.
14. Production smoke tests.
15. Sophisticated re-ingestion reconciliation or historical dataset comparison.

Teams should prioritize completing, testing, and integrating the Sprint 2 review-intelligence requirements before implementing Sprint 3 deployment functionality.