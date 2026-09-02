# Sprint 1 Demo Script (Fall 2026)

_ReviewLens AI - CS 490 Capstone_

## 1. Purpose

This document defines exactly how teams should prepare for and run the Sprint 1 ReviewLens AI demonstration.

The Sprint 1 demo is intended to show that the team has built a working, test-backed application foundation that includes:

1. Managed authentication.
2. Reproducible development setup.
3. User-owned AnalysisTargets.
4. Review ingestion and persistence.
5. Cross-user authorization protection.
6. Automated testing and continuous integration.

The demo should be presented as one coherent application workflow rather than as a sequence of Jira tickets.

The instructor may ask technical questions at any point during the demonstration. Questions are part of the demo and do not stop the clock.

---

## 2. Hard Time Limit

The Sprint 1 demo has a **20-minute hard cap**.

The 20-minute clock includes:

1. Application startup or loading.
2. Switching accounts.
3. Instructor questions.
4. Navigation between application screens.
5. Opening tests or CI evidence.
6. Recovery from application or environment problems.
7. Any other setup performed after the demo begins.

**The demo ends at 20 minutes whether or not every required item has been shown.**

Any required behavior not demonstrated before time expires is considered not demonstrated.

Teams are expected to rehearse the complete demo and prepare all required data, accounts, browser tabs, terminals, tools, and evidence before class.

A prepared team should be able to complete this demo comfortably within the time limit.

---

## 3. Required Demo Preparation

Lack of preparation can substantially affect the demo result.

Do not use demo time to:

1. Create test accounts.
2. Search for suitable review data.
3. Find a target URL.
4. Configure authentication.
5. Install packages.
6. Repair environment configuration.
7. Locate tests.
8. Search through CI history.
9. Determine how to demonstrate a security requirement.
10. Decide which team member will perform each part of the demo.

Everything needed for the demonstration should be prepared before the team is called.

### 3.1 Required User Accounts

Prepare **two working registered accounts**.

#### User A — Primary Demo Account

User A should have:

1. At least **two AnalysisTargets** before the demo begins.
2. At least one AnalysisTarget with a previously successful ingestion.
3. At least one persisted dataset containing approximately **15-20 or more real reviews**.
4. Review data containing meaningful written review text and ratings.
5. A known AnalysisTarget URL or resource identifier that can later be used during the cross-user security demonstration.

One additional AnalysisTarget may be created live during the demo.

#### User B — Security / Isolation Account

User B should have:

1. At least **one AnalysisTarget**.
2. A small but meaningful persisted review dataset, approximately **5-10 or more real reviews**.
3. Data that is clearly distinct from User A's data.

User B primarily exists to demonstrate that ReviewLens correctly isolates data between authenticated users.

### 3.2 Required Demo Data

The demo should begin with meaningful persisted data already available.

At minimum:

1. User A must have one previously ingested dataset containing approximately 15-20 or more reviews.
2. User B must have a smaller, distinct persisted dataset containing approximately 5-10 or more reviews.
3. The datasets should contain enough realistic review text and rating variation to make ownership and persistence obvious.
4. The team should know exactly which AnalysisTargets and datasets will be shown during the demo.

Do not begin the demo with empty accounts and attempt to manufacture all required data live.

### 3.3 Required Ingestion Inputs

Prepare:

1. One known-valid review source or supported review-data input for the live ingestion demonstration.
2. One known-invalid or unusable source/input for the ingestion failure demonstration.
3. One previously ingested dataset that can be used as fallback evidence if the live third-party source is temporarily unavailable.

The fallback dataset does not replace the requirement to implement real ingestion.

If a third-party review service or website is unavailable during the demo, the team may use previously ingested data to continue the demonstration, but the team must still be able to show and explain the implemented ingestion path.

Hard-coded fake reviews do not satisfy the ingestion requirement.

### 3.4 Required Testing and CI Evidence

Before the demo begins, identify and be ready to show:

1. One negative authentication or authorization test.
2. One negative validation test.
3. One negative ingestion or normalization test.
4. A recent successful CI workflow.
5. Evidence that required checks include:
   - lint/static checks
   - build
   - automated tests
6. Evidence that failing required checks block the normal merge workflow.

Relevant CI pages, pull requests, tests, and repository files should already be easy to reach.

### 3.5 Team Environment Readiness

Every team member is expected to have a working development environment capable of:

1. Pulling the current codebase.
2. Installing required dependencies.
3. Running the application.
4. Running the automated tests.
5. Accessing required development services.
6. Using the documented environment configuration.

The project should not depend on a single **"magic laptop"** that is the only machine capable of running the system.

The instructor may select any team member's computer as the demonstration device.

For Sprint 1, the team may ultimately be allowed to use its preferred device, but every team member should prepare as though their device could be selected.

### 3.6 Demo Readiness and Rehearsal

The team should arrive knowing:

1. Which account will be used at each step.
2. Which AnalysisTarget will be used.
3. Which review source will be used.
4. Which invalid input will be used.
5. Which resource identifier will be used for the cross-user attack.
6. Which tests will be shown.
7. Which CI workflow will be shown.
8. Which team member will explain each major area.

Avoidable preparation problems may prevent required behavior from being demonstrated before the hard time limit.

Examples include:

1. Required accounts do not exist.
2. Demo data has not been prepared.
3. The team cannot find a suitable review source.
4. Credentials or environment variables have not been configured.
5. Only one developer can run the application.
6. Tests cannot be located or run.
7. CI evidence cannot be found.
8. The team has not rehearsed the security demonstration.
9. The team spends demo time deciding what to show next.

These are preventable engineering and preparation problems, not reasons to extend the demo time.

The complete demonstration should be rehearsed before demo day and should fit comfortably within the 20-minute hard cap.

---

## 4. Before the Clock Starts

Before the team is called:

1. Confirm that the application runs.
2. Confirm that required backend services are available.
3. Confirm that User A and User B credentials work.
4. Confirm that the valid ingestion source still works when practical.
5. Confirm that prepared datasets exist.
6. Confirm that required tests pass.
7. Confirm that the CI evidence is available.
8. Open any browser tabs, terminals, API tools, or repository pages that will be needed.
9. Decide who controls the keyboard.
10. Decide which team member explains each major part of the system.

Do not begin the demonstration by explaining the project history or presenting a slide deck.

Start with the working application.

---

## 5. Live Demo Script

The sequence below is the expected Sprint 1 demonstration order.

Approximate times are provided to help teams rehearse. They are not separate time allocations that pause when the instructor asks a question.

A well-prepared team should target approximately **16-17 minutes of planned demonstration**, leaving several minutes within the hard cap for instructor questions.

### Step 1 — Start Unauthenticated and Demonstrate Protected Access

**Target time: approximately 1 minute**

Begin with ReviewLens in a logged-out state.

Show:

1. The ReviewLens application loads.
2. An attempt is made to navigate directly to protected ReviewLens functionality.
3. The application denies access or redirects appropriately.
4. If practical, briefly demonstrate that a protected backend request also rejects unauthenticated access.

Then authenticate as **User A** using the team's selected managed identity provider.

The team does **not** need to demonstrate:

1. Password-policy implementation.
2. Password storage.
3. Duplicate-email handling.
4. Password-reset internals.
5. Other functionality supplied directly by the managed identity provider.

Be prepared to explain:

- Which managed authentication provider the team selected.
- What security responsibilities are handled by that provider.
- What security responsibilities remain in the ReviewLens application.

### Step 2 — Show User A's Existing Data

**Target time: approximately 1 minute**

Open User A's AnalysisTarget list.

Show that User A already has meaningful persisted application data.

Identify at least one existing target and briefly show:

1. Target/entity name.
2. Supported review platform.
3. Source URL or source reference.
4. Existing ingestion state.
5. That the target has persisted review data.

Do not spend time reading individual reviews aloud.

The purpose of this step is to establish that ReviewLens contains persistent application data and is not operating only from temporary in-memory demo state.

### Step 3 — Demonstrate AnalysisTarget Validation and Creation

**Target time: approximately 2-3 minutes**

Create a new AnalysisTarget.

First, intentionally submit invalid input.

Examples include:

1. Missing required target name.
2. Missing source information.
3. Malformed URL.
4. Source input that clearly does not satisfy the team's supported format.

Show that:

1. The invalid target is rejected.
2. The user receives a meaningful application-level validation message.
3. The message is understandable to an average user.
4. No invalid target is persisted.

Do not present raw exceptions, stack traces, database messages, or third-party provider error text as normal user-facing validation.

Correct the input and create the AnalysisTarget successfully.

Then demonstrate persistence by doing one of the following:

1. Refresh the page.
2. Navigate away and return.
3. Reopen the target from the AnalysisTarget list.

Show that the new target still exists.

Open the target's Analysis Workspace.

The workspace should clearly identify:

1. Target/entity name.
2. Review platform.
3. Source reference.
4. Basic current ingestion state.
5. The available ingestion action.

### Step 4 — Perform Live Review Ingestion

**Target time: approximately 3-4 minutes**

From the newly created or selected AnalysisTarget, initiate ingestion using the team's supported method.

The team may use:

1. A publicly accessible review URL.
2. A supported import format.
3. Another approved ingestion mechanism.

Show enough of the workflow to establish that ReviewLens obtains real review data rather than substituting hard-coded demo content.

After ingestion, show representative persisted Review records.

At minimum, demonstrate that ReviewLens captured:

1. Written review text.
2. Rating.

If the team preserves additional metadata, briefly identify it, such as:

1. Reviewer/display name.
2. Review date.
3. Source review ID.
4. Source URL.
5. Other useful platform-specific metadata.

The team should briefly explain:

1. What the source-specific ingestion layer receives.
2. How raw source data becomes the application's canonical Review representation.
3. Where normalized Reviews are persisted.

Show that:

1. The Reviews belong to the correct AnalysisTarget.
2. The ingestion operation records a successful result state.
3. Reloading or navigating away does not cause the ingested Reviews to disappear.

Do not spend demo time scrolling through large numbers of reviews.

Several representative records plus counts or persistence evidence are sufficient.

#### External Source Failure During the Demo

If the third-party review source unexpectedly becomes unavailable:

1. Show that the application handles the failure correctly if possible.
2. Do not spend several minutes retrying the same external operation.
3. Move to the prepared previously ingested dataset.
4. Continue the demo using that data.

The team must still be able to explain the implemented ingestion path and show evidence that it has operated successfully.

### Step 5 — Demonstrate Ingestion Failure Handling

**Target time: approximately 1-2 minutes**

Use the prepared invalid or unusable ingestion input.

Show that:

1. The ingestion attempt fails cleanly.
2. The user receives a meaningful error message.
3. The message is appropriate for an average application user.
4. The application does not display raw exception text as its normal error experience.
5. ReviewLens does not fabricate review records.
6. Existing valid persisted review data remains intact.

Examples of poor user-facing failure behavior include:

- raw stack traces
- database exception messages
- HTTP client exceptions
- provider authentication errors copied directly to the screen
- generic unhandled-error pages with no useful application guidance

The application may log technical diagnostic information internally. That technical information should not be confused with the user-facing error experience.

Be prepared to explain how the ingestion code handles:

1. Invalid source data.
2. Unexpected source responses.
3. Third-party failure.

### Step 6 — Demonstrate Cross-User Authorization

**Target time: approximately 2-3 minutes**

This step must demonstrate **backend authorization**, not merely frontend filtering.

#### Part A — Identify User A's Resource

While authenticated as **User A**:

1. Identify a specific AnalysisTarget owned by User A.
2. Copy or note its direct URL or resource identifier.

For example:

`/analysis-targets/abc123`

The exact URL structure is determined by the team's application.

#### Part B — Switch to User B

1. Log out of User A.
2. Authenticate as **User B**.
3. Open User B's AnalysisTarget list.
4. Briefly show that User B has their own distinct AnalysisTargets and data.

The fact that User A's target is not displayed in User B's normal list is **not sufficient** evidence of authorization.

#### Part C — Deliberately Request User A's Known Resource

While still authenticated as User B:

1. Directly request User A's known AnalysisTarget using the URL or resource identifier captured earlier.
2. Show that access is denied.
3. Show that User A's target data is not returned.

If the application architecture does not expose resource identifiers in browser routes, demonstrate the equivalent request using one of the following:

1. Browser developer tools.
2. Postman.
3. curl.
4. Another API client.

The important evidence is:

> User B deliberately requests a known, valid User A resource, and backend or persistence-layer authorization prevents access.

Do not rely only on hidden buttons, frontend filtering, or the absence of User A records from User B's list.

The live demonstration only needs to show one clear cross-user attack.

Automated tests should cover additional ownership cases such as:

1. Cross-user review access.
2. Cross-user mutation attempts.
3. Cross-user ingestion attempts.

### Step 7 — Show Representative Automated Tests

**Target time: approximately 2 minutes**

Open the prepared automated tests.

Show and briefly explain at least three negative tests:

#### Test 1 — Authentication or Authorization

Examples:

1. Unauthenticated request to a protected backend endpoint fails.
2. User B cannot retrieve User A's AnalysisTarget.
3. User B cannot ingest reviews into User A's target.

#### Test 2 — Validation

Examples:

1. Missing target name is rejected.
2. Invalid source URL is rejected.
3. Required target information is not persisted when invalid.

#### Test 3 — Ingestion or Normalization

Examples:

1. Malformed review record is rejected or skipped according to team rules.
2. Review without required text is handled correctly.
3. Invalid rating is handled correctly.
4. External ingestion failure produces the expected application result.

For each test, briefly answer:

> **What defect or security failure is this test intended to prevent?**

Do not spend demo time scrolling through the entire test suite or discussing test counts.

The objective is to demonstrate thoughtful automated verification of meaningful behavior.

### Step 8 — Show Continuous Integration Evidence

**Target time: approximately 1-2 minutes**

Open the team's CI system.

Show a recent relevant pull request or workflow run.

Demonstrate that CI includes:

1. Lint or equivalent static checks.
2. Application build.
3. Automated tests.

Show evidence that required checks must pass before the team's normal merge workflow can complete.

Acceptable evidence may include:

1. Protected branch configuration.
2. Required status checks.
3. A previous pull request blocked by a failing check.
4. Equivalent repository workflow controls.

The team does not need to intentionally break the application during the live demo.

Be prepared to explain:

1. What happens when a required test fails.
2. Whether developers can normally merge while required checks are failing.
3. How the team knows which check failed.

### Step 9 — Close the Demo

**Target time: approximately 30 seconds**

Conclude with two brief statements:

1. What the Sprint 1 application can now accomplish end-to-end.
2. What the team considers its largest technical risk entering Sprint 2.

Do not repeat the entire demo or present a summary slide deck.

---

## 6. Instructor Questions During the Demo

The instructor may ask questions at any point.

Questions may address:

1. Architecture.
2. Data modeling.
3. Authentication and authorization.
4. Review ingestion.
5. Error handling.
6. Testing.
7. CI/CD.
8. Technical tradeoffs.
9. Team design decisions.
10. Code written or modified by a specific team member.

The team member responsible for the relevant area should normally answer.

The instructor may ask to see code, tests, API behavior, persistence behavior, or configuration when needed to clarify what is being demonstrated.

**The demo clock continues while questions are being answered.**

Teams should therefore understand their implementation well enough to answer technical questions concisely.

---

## 7. Final Preparation Checklist

Before demo day, confirm all of the following:

- [ ] User A account works.
- [ ] User B account works.
- [ ] User A has at least two AnalysisTargets.
- [ ] User A has a persisted dataset with approximately 15-20+ real reviews.
- [ ] User B has at least one AnalysisTarget.
- [ ] User B has a small but meaningful persisted dataset.
- [ ] A valid ingestion source/input is prepared.
- [ ] An invalid ingestion source/input is prepared.
- [ ] A previously successful ingestion is available as fallback.
- [ ] A User A target URL/resource ID is known for the security demo.
- [ ] Authentication/authorization negative test is identified.
- [ ] Validation negative test is identified.
- [ ] Ingestion/normalization negative test is identified.
- [ ] Latest relevant CI workflow is easy to access.
- [ ] Merge-protection evidence is easy to access.
- [ ] Required engineering/context documents are committed.
- [ ] Every team member can build, test, and run the application.
- [ ] All required environment configuration is complete.
- [ ] Demo browser tabs/tools are prepared.
- [ ] Team members know who will explain each area.
- [ ] The complete demonstration has been rehearsed within the 20-minute hard cap.
