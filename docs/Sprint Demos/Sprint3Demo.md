# Sprint 3 Demo Script (Fall 2026)

_ReviewLens AI - CS 490 Capstone_

## 1. Purpose

This document defines exactly how teams should prepare for and run the Sprint 3 ReviewLens AI demonstration.

Sprint 3 is the final production increment of the capstone. The demo should show that ReviewLens is no longer dependent on a developer's local environment and now operates as a small production software system.

The demo should show:

1. A publicly reachable production application.
2. Automated deployment through the team's CI/CD process.
3. Protected production configuration and secrets.
4. Persisted ReviewLens data that survives across sessions and deployments.
5. Production-safe application lifecycle behavior.
6. Graceful handling of external-service failures.
7. Post-deployment health checks and smoke tests.
8. Security/dependency scanning.
9. Continued authentication, authorization, ingestion-summary, grounded-Q&A, and scope-guard behavior in production.

The demo should be presented as one coherent production ReviewLens workflow rather than as a sequence of Jira tickets.

The instructor may ask technical questions at any point during the demonstration. Questions are part of the demo and do not stop the clock.

---

## 2. Hard Time Limit

The Sprint 3 demo has a **20-minute hard cap**.

The clock includes:

1. Accessing the production application.
2. Switching accounts.
3. Instructor questions.
4. Waiting for model responses.
5. Opening CI/CD, deployment, health, smoke-test, migration, or security evidence.
6. Recovery from application or production-environment problems.
7. Any other setup performed after the demo begins.

**The demo ends at 20 minutes whether or not every required item has been shown.**

Any required behavior not demonstrated before time expires is considered not demonstrated.

Teams are expected to rehearse the complete production demonstration and prepare all required accounts, data, test resources, browser tabs, pipeline evidence, and operational evidence before class.

A prepared team should target approximately **16-17 minutes of planned demonstration**, leaving room for instructor questions.

---

## 3. Required Demo Preparation

Everything needed for the Sprint 3 demonstration should be prepared before the team is called.

The deployed ReviewLens application should already be running and should not require a deployment during the demo simply to become usable.

### 3.1 Required Production Environment

Prepare:

1. A publicly reachable production URL.
2. A production environment that is already operational before the demo begins.
3. Working production authentication.
4. Working production persistence.
5. Working production LLM access.
6. Working production access to the team's review ingestion mechanism or previously persisted real review data.
7. Production configuration that is separate from development and test configuration.

The primary application demonstration must use the **deployed production environment**, not a developer's local application instance.

A local development environment may be used to show source code or local test files, but it is not a substitute for the production application.

### 3.2 Required Production Accounts and Data

Prepare **two working production accounts**.

#### User A — Primary Production Demo Account

User A should have:

1. At least **two persisted AnalysisTargets**.
2. At least one AnalysisTarget created in an earlier session and still available in production.
3. At least one target with meaningful real persisted review data.
4. A usable ingestion summary.
5. A dataset suitable for grounded Q&A and scope-guard demonstration.
6. One disposable AnalysisTarget that can be safely deleted during the demo.

As a guideline, the primary dataset should contain approximately **20 or more real reviews**.

#### User B — Security / Isolation Account

User B should have:

1. At least one AnalysisTarget.
2. A distinct persisted review dataset.
3. Data that is clearly distinguishable from User A's data.

Prepare one known User A AnalysisTarget URL or identifier that can be used to demonstrate that production authorization still prevents User B from accessing User A's data.

### 3.3 Required Production Lifecycle Evidence

Prepare:

1. A persisted AnalysisTarget that can be reopened from an earlier session.
2. A disposable User A AnalysisTarget that can be deleted safely.
3. Evidence that cross-user deletion is denied.
4. If the team supports re-ingestion:
   - an existing target that can be re-ingested safely, and
   - a clear explanation of how new ingestion affects the current dataset.
5. If the team does **not** support re-ingestion:
   - the instructor-approved equivalent production-lifecycle behavior that replaces that story.

Do not use important production data as the deletion demonstration target.

### 3.4 Required Production Failure Evidence

Prepare evidence for both of these failure classes:

1. **Review ingestion/external source failure**
2. **LLM provider failure**

The evidence may combine:

1. A safe live failure case in the deployed application.
2. Automated tests that simulate the external dependency failure.
3. Controlled failure-injection or mocked-provider evidence.
4. Relevant production-safe logs or pipeline evidence.

The team should be able to show that failures:

1. Produce meaningful user-facing behavior.
2. Do not expose raw secrets or unnecessary internal details.
3. Do not fabricate successful ingestion or AI analysis.
4. Do not silently destroy previously valid persisted data.

Do not intentionally cause a destructive production outage merely for the demo.

### 3.5 Required CI/CD and Deployment Evidence

Before the demo begins, identify and be ready to show:

1. A recent successful production deployment.
2. The commit or merge that triggered that deployment.
3. The required CI quality gates that completed before deployment.
4. Evidence that a failing required gate prevents normal deployment.
5. Evidence of a failed deployment or failed release stage when available, showing that failure is visible.
6. The automated post-deployment health verification.
7. The automated production smoke-test suite.
8. Security or dependency scanning.
9. Schema/migration verification appropriate to the team's persistence technology.
10. Evidence that production configuration and secrets are provided through appropriate protected mechanisms.

Do **not** display actual secret values during the demo.

### 3.6 Required Production Smoke-Test Data

Prepare any dedicated test account, AnalysisTarget, fixture, or controlled production data needed by the smoke-test suite.

Smoke tests must be:

1. Safe to run repeatedly.
2. Non-destructive to real user data.
3. Small enough to run as deployment verification rather than duplicating the complete automated test suite.

The team should know which smoke tests verify:

1. Application health or availability.
2. Protected access.
3. Review data or ingestion-summary behavior.
4. Grounded Q&A.
5. Scope-guard behavior.

### 3.7 Demo Readiness and Rehearsal

The team should arrive knowing:

1. Which production account is used at each step.
2. Which persisted target will be reopened.
3. Which target will be used for Q&A.
4. Which disposable target will be deleted.
5. Which User A resource will be used for the User B authorization check.
6. Which failure evidence will be shown.
7. Which successful production deployment will be shown.
8. Which health-check and smoke-test run will be shown.
9. Which security scan will be shown.
10. Which migration/schema evidence will be shown.
11. Which team member will explain each major area.

Avoidable preparation problems are not reasons to extend the demo.

---

## 4. Before the Clock Starts

Before the team is called:

1. Confirm that the public production URL works.
2. Confirm that User A and User B can authenticate in production.
3. Confirm that prepared persisted targets and review data exist.
4. Confirm that the prepared Q&A questions still behave as expected.
5. Confirm that the disposable deletion target exists.
6. Confirm that required CI/CD and deployment evidence is available.
7. Confirm that health-check and smoke-test evidence is available.
8. Confirm that security-scan evidence is available.
9. Confirm that migration/schema evidence is available.
10. Open any browser tabs, pipeline pages, logs, test files, or repository files that will be needed.

Do not begin with a slide deck or project-history presentation.

Start with the publicly deployed application.

---

## 5. Live Demo Script

The sequence below is the expected Sprint 3 demonstration order.

### Step 1 — Open the Public Production Application

**Target time: approximately 1 minute**

Open the public ReviewLens production URL.

Begin logged out.

Show:

1. The production application is reachable.
2. Protected ReviewLens functionality still requires authentication.
3. User A can authenticate successfully in production.

Briefly identify the hosting/deployment platform.

Do not spend time re-demonstrating managed-authentication features already established in Sprint 1.

### Step 2 — Reopen Persisted Production Data

**Target time: approximately 2 minutes**

Using User A:

1. Open the AnalysisTarget list.
2. Select the prepared target created during an earlier session.
3. Show that the target still exists.
4. Show its persisted review data.
5. Show its ingestion state.
6. Show its ingestion summary.

Demonstrate that the application does not require re-ingestion merely because the browser session ended or a new deployment occurred.

Be prepared to explain where production data is stored and how the deployed application connects to it.

### Step 3 — Demonstrate the Production ReviewLens Workflow

**Target time: approximately 2-3 minutes**

Using the persisted target:

1. Show the ingestion summary.
2. Ask one prepared in-scope review question.
3. Show a grounded answer based on the production review dataset.
4. Ask one prepared out-of-scope question.
5. Show the production scope guard decline it.

This is a regression check of the major Sprint 2 behavior.

Do not repeat the full Sprint 2 demonstration.

The purpose is to establish that the deployed production system still behaves as ReviewLens.

### Step 4 — Demonstrate Production Lifecycle and Authorization

**Target time: approximately 2-3 minutes**

#### Part A — Delete an Owned Disposable Target

Using User A:

1. Open the prepared disposable AnalysisTarget.
2. Delete it.
3. Show that it is no longer normally accessible.
4. Briefly explain what happens to associated reviews and ingestion data.

The team should know whether its design uses:

1. Cascading deletion.
2. Soft deletion.
3. Another documented strategy.

#### Part B — Demonstrate Cross-User Protection

Identify or use the prepared URL/identifier for a different User A target that must remain intact.

Then:

1. Log out of User A.
2. Authenticate as User B.
3. Deliberately request the known User A resource.
4. Show that production authorization denies access.

If the team has an automated cross-user deletion test, be prepared to show it as supporting evidence.

### Step 5 — Demonstrate Re-Ingestion or Approved Equivalent Lifecycle Behavior

**Target time: approximately 1-2 minutes**

If the team supports re-ingestion:

1. Open the prepared existing AnalysisTarget.
2. Initiate or show evidence of a new ingestion run.
3. Show that the application clearly distinguishes the new result from prior ingestion state.
4. Explain whether the strategy replaces, merges, or otherwise reconciles review data.
5. Show or explain how a failed re-ingestion avoids destroying previously valid data.

If the team deliberately does not support re-ingestion, demonstrate the instructor-approved equivalent production-lifecycle story instead.

### Step 6 — Demonstrate Production Failure Handling

**Target time: approximately 2 minutes**

Show prepared evidence for both:

1. Review ingestion/external source failure.
2. LLM provider failure.

For each failure, demonstrate or show test evidence that ReviewLens:

1. Produces meaningful user-facing behavior.
2. Does not display raw exception details as the normal user experience.
3. Does not expose secrets.
4. Does not fabricate successful results.
5. Preserves previously valid data where applicable.

Be prepared to explain where technical diagnostic information is logged.

### Step 7 — Show the Automated Production Release Pipeline

**Target time: approximately 3 minutes**

Open a recent successful release workflow.

Trace the release from source change to production.

Show that:

1. Required Sprint 1 and Sprint 2 quality gates run before deployment.
2. Required Sprint 3 security/dependency checks run.
3. Deployment occurs automatically from the protected release branch or equivalent workflow.
4. The deployment identifies the commit being released.
5. A failing required quality gate prevents normal deployment.
6. Deployment failure is visible when it occurs.

The team does not need to intentionally break production during the demo.

A prior failed workflow or controlled branch failure is sufficient evidence.

### Step 8 — Show Production Configuration, Migration, and Security Evidence

**Target time: approximately 1-2 minutes**

Show enough configuration evidence to establish that production is configured separately and securely.

Demonstrate:

1. Required production configuration names or masked configuration entries.
2. Server-side secrets are not committed to source control or exposed to the browser.
3. Development/test/production configuration can differ without source-code edits.

Then show:

1. Migration/schema-management evidence appropriate to the team's persistence technology.
2. The security/dependency scan and how findings are reviewed.

Do not display actual secret values.

### Step 9 — Show Post-Deployment Health and Smoke Tests

**Target time: approximately 2 minutes**

Show the automated post-deployment verification associated with a recent release.

Demonstrate:

1. Health verification ran against the deployed application.
2. Smoke tests ran against the deployed or production-equivalent environment.
3. The smoke suite verifies representative critical behavior.
4. The smoke suite is safe to run repeatedly.
5. A failed required post-deployment verification produces a visible release failure.

Identify which smoke tests cover:

1. Protected access.
2. Review data or ingestion summary.
3. Grounded Q&A.
4. Scope-guard behavior.

The smoke suite should be intentionally smaller than the complete test suite.

### Step 10 — Close the Demo

**Target time: approximately 30 seconds**

Conclude with two brief statements:

1. What makes the current ReviewLens implementation production-ready compared with Sprint 2.
2. One significant improvement the team would make if development continued beyond the capstone.

Do not repeat the full demonstration or present a summary slide deck.

---

## 6. Instructor Questions During the Demo

The instructor may ask questions at any point.

Questions may address:

1. Hosting and deployment architecture.
2. CI/CD dependencies and release gating.
3. Production configuration and secret handling.
4. Database migrations or schema management.
5. Production persistence.
6. Failure handling.
7. Logging.
8. Security/dependency scanning.
9. Smoke-test design.
10. Health-check design.
11. User-ownership enforcement in production.
12. Q&A and scope-guard regression behavior.
13. Operational tradeoffs.
14. Code or configuration written or modified by a specific team member.

The team member responsible for the relevant area should normally answer.

The instructor may ask to see code, pipeline configuration, deployment logs, tests, health checks, security findings, or migration artifacts when needed to clarify what is being demonstrated.

**The demo clock continues while questions are being answered.**

---

## 7. Final Preparation Checklist

Before demo day, confirm all of the following:

- [ ] Public production URL is operational.
- [ ] Production authentication works.
- [ ] User A production account works.
- [ ] User B production account works.
- [ ] User A has persisted AnalysisTargets from an earlier session.
- [ ] User A has meaningful persisted real review data.
- [ ] User B has distinct persisted data.
- [ ] A disposable User A target is prepared for deletion.
- [ ] A User A target URL/resource ID is known for the User B authorization check.
- [ ] Re-ingestion example or approved equivalent lifecycle behavior is prepared.
- [ ] Ingestion/external-source failure evidence is prepared.
- [ ] LLM-provider failure evidence is prepared.
- [ ] Recent successful deployment workflow is identified.
- [ ] Failed quality-gate/deployment evidence is identified.
- [ ] Production health-check evidence is identified.
- [ ] Production smoke-test evidence is identified.
- [ ] Security/dependency-scan evidence is identified.
- [ ] Migration/schema-management evidence is identified.
- [ ] Production configuration evidence is ready without exposing secrets.
- [ ] Smoke-test data is safe and repeatable.
- [ ] Demo browser tabs/tools are prepared.
- [ ] Team members know who will explain each area.
- [ ] The complete production demonstration has been rehearsed within the 20-minute hard cap.
