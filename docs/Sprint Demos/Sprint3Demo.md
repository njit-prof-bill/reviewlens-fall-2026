# Sprint 3 Demo Script (Fall 2026)

_ReviewLens AI - CS 490 Capstone_

## 1. Purpose

This document defines how teams should prepare for and run the final Sprint 3 ReviewLens demonstration.

Sprint 3 should show that ReviewLens has become a complete, usable product.

The demo should emphasize:

1. Saved-analysis lifecycle.
2. Persistent Q&A history.
3. Review refresh/re-ingestion.
4. Evidence-backed analysis.
5. Review browsing and filtering.
6. CSV and Markdown export.
7. Continued user isolation.
8. Public deployment.

The application itself must be demonstrated from its **public web URL**.

The instructor may ask technical questions at any point. Questions are part of the demo and do not stop the clock.

## 2. Hard Time Limit

The Sprint 3 demo has a **20-minute hard cap**.

The clock includes authentication, navigation, instructor questions, waiting for ingestion or AI responses, opening test or CI evidence, inspecting exports, and recovery from unexpected problems.

**The demo ends at 20 minutes whether or not every required item has been shown.**

Any required behavior not demonstrated before time expires is considered not demonstrated.

Teams should target approximately **16-17 minutes of planned demonstration**, leaving room for instructor questions.

## 3. Required Demo Preparation

Everything needed for the demonstration should be prepared before the team is called.

### 3.1 Public Application

Prepare:

1. A working public ReviewLens URL.
2. Working production authentication.
3. Working persistent storage.
4. Working Q&A access.
5. Working export functionality.

The primary application demo must use the public deployment.

Do not run the ReviewLens application from a developer laptop for the final demo.

### 3.2 Required Accounts

Prepare two working accounts.

#### User A - Primary Demo Account

User A should have:

1. At least two saved analyses.
2. At least one analysis created during an earlier session.
3. A meaningful persisted review dataset.
4. Persisted Q&A history.
5. A dataset suitable for evidence-backed Q&A.
6. One analysis safe to rename or copy.
7. One disposable analysis safe to delete.

#### User B - Isolation Account

User B should have:

1. At least one saved analysis.
2. A distinct persisted review dataset.

Prepare one known User A analysis URL or identifier for the user-isolation demonstration.

### 3.3 Required Review Data

Prepare an analysis with enough real review data to demonstrate:

1. Ingestion summary.
2. Grounded Q&A.
3. Supporting evidence.
4. Complete review browsing.
5. Rating filtering.
6. Date filtering when source dates exist.
7. CSV export.
8. Markdown export.

As a guideline, use approximately **20 or more real reviews**.

### 3.4 Required Q&A History

Prepare a saved analysis with at least two persisted question/response pairs.

At least one grounded answer should have supporting review evidence.

### 3.5 Required Re-Ingestion Input

Prepare an existing analysis that can be refreshed safely.

The team should know:

1. The current review count before refresh.
2. The expected behavior after refresh.
3. The team's duplicate-prevention strategy.
4. How the application protects the current dataset if refresh fails.

Because public review sources can change or become unavailable, also prepare automated test evidence for failed refresh behavior.

### 3.6 Required Export Evidence

Prepare to generate:

1. One CSV export of the active review dataset.
2. One Markdown export of the active analysis.

Know where downloaded files will appear so demo time is not spent searching for them.

### 3.7 Required Test and CI Evidence

Identify before the demo:

1. A test for Save As or analysis lifecycle.
2. A Q&A-history persistence test.
3. A re-ingestion duplicate-prevention test.
4. A failed-refresh preservation test.
5. A supporting-evidence ownership/association test.
6. An export test.
7. A recent successful CI run.

Sprint 1 and Sprint 2 test and CI requirements remain in force.

### 3.8 Demo Readiness and Rehearsal

The team should know:

1. Which saved analysis will be reopened.
2. Which analysis will be renamed.
3. Which analysis will be used for Save As.
4. Which analysis will be refreshed.
5. Which grounded question will demonstrate supporting evidence.
6. Which filters will be applied.
7. Which exports will be generated.
8. Which disposable analysis will be deleted.
9. Which User A resource will be used for the User B isolation check.
10. Which tests and CI run will be shown.

Avoidable preparation problems are not reasons to extend the demo.

## 4. Before the Clock Starts

Before the team is called:

1. Confirm that the public URL works.
2. Confirm that User A and User B can authenticate.
3. Confirm that prepared saved analyses exist.
4. Confirm that Q&A history exists.
5. Confirm that review evidence is available.
6. Confirm that the re-ingestion source is usable when practical.
7. Confirm that exports work.
8. Confirm that required tests pass.
9. Confirm that CI evidence is available.
10. Open any repository/test/CI pages that will be needed.

Start with the public ReviewLens application.

Do not begin with a slide deck.

## 5. Live Demo Script

### Step 1 - Open the Public Application and Reopen a Saved Analysis

**Target time: approximately 1-2 minutes**

Open the public ReviewLens URL and authenticate as **User A**.

Use the left analysis sidebar to reopen an analysis created during an earlier session.

Show that the analysis restores:

1. Human-readable analysis name.
2. Entity/source context.
3. Current review dataset.
4. Ingestion summary.
5. Persisted Q&A history.

### Step 2 - Demonstrate Rename and Save As

**Target time: approximately 2 minutes**

Rename one owned analysis.

Show that:

1. The new name appears in the analysis sidebar.
2. The source URL and review data remain unchanged.

Then use **Save As** on a prepared analysis and give the copy a new name.

Show that:

1. The original remains intact.
2. The copy has a separate analysis identity.
3. The copy has the expected current review dataset.
4. A later rename of the copy does not rename the original.

### Step 3 - Show Persistent Q&A History

**Target time: approximately 1 minute**

Open the prepared analysis containing prior Q&A.

Show at least two previously persisted question/response pairs.

Briefly demonstrate that switching to another analysis changes the visible Q&A history appropriately.

Return to the primary analysis.

### Step 4 - Demonstrate Evidence-Backed Q&A

**Target time: approximately 2-3 minutes**

Ask a prepared in-scope question.

Show that ReviewLens produces a grounded answer and displays supporting review evidence.

If the application provides a **View matching reviews** or equivalent action, open it.

Be prepared to explain:

1. How supporting reviews are selected.
2. How ReviewLens ensures they belong to the active AnalysisTarget.
3. How review identity is preserved between retrieval and presentation.

Do not present a numerical confidence score unless the team has a defensible method for calculating it.

### Step 5 - Browse and Filter the Review Dataset

**Target time: approximately 2 minutes**

Open the complete review dataset for the active analysis.

Show representative review fields such as:

1. Rating.
2. Review text.
3. Date when available.
4. Reviewer/display name when available.

Apply:

1. A rating filter.
2. A date/date-range filter when source dates are available.

Show that the results change appropriately and remain scoped to the active analysis.

### Step 6 - Refresh / Re-Ingest the Existing Analysis

**Target time: approximately 2-3 minutes**

Open the prepared existing analysis and initiate a refresh/re-ingestion.

Show:

1. The user does not need to create a new analysis.
2. A new ingestion attempt is recorded.
3. Successful refresh updates the current dataset and ingestion summary.
4. Duplicate source reviews are not silently multiplied.

If the external review source is too slow or unavailable, use prepared successful-refresh evidence and continue.

Be prepared to show automated test evidence proving:

1. Duplicate prevention.
2. A failed refresh preserves the last known-good dataset.

### Step 7 - Export the Analysis

**Target time: approximately 2 minutes**

From the active analysis:

1. Export the current review dataset to CSV.
2. Show the downloaded filename.
3. Briefly inspect the file to verify representative review data.

Then:

1. Export the analysis to Markdown.
2. Show the downloaded filename.
3. Briefly inspect the document.

The Markdown export should contain useful analysis context such as analysis name, entity/source information, ingestion summary, Q&A history when present, and supporting evidence when associated with saved Q&A.

### Step 8 - Delete an Owned Analysis

**Target time: approximately 1 minute**

Delete the prepared disposable analysis or Save As copy.

Show:

1. Clear confirmation of destructive intent.
2. The analysis disappears from normal retrieval.
3. The team can briefly explain how associated data is handled.

Do not delete the primary demonstration dataset.

### Step 9 - Confirm Multi-User Isolation on the Public Application

**Target time: approximately 1 minute**

Identify a known User A analysis URL or identifier.

Log out and authenticate as **User B**.

Deliberately attempt to access the User A analysis.

Show that access is denied.

The fact that User A's analysis is absent from User B's sidebar is not, by itself, sufficient evidence.

### Step 10 - Show Representative Tests and CI

**Target time: approximately 2 minutes**

Show a small number of representative Sprint 3 tests.

Include evidence for:

1. Q&A-history persistence or analysis lifecycle.
2. Re-ingestion duplicate prevention or failed-refresh preservation.
3. Supporting-evidence association/ownership.
4. Export behavior.

Then show a recent successful CI run demonstrating that the established required quality gates still pass.

Do not scroll through the entire test suite.

### Step 11 - Close the Demo

**Target time: approximately 30 seconds**

Conclude with two brief statements:

1. What Sprint 3 added that makes ReviewLens feel like a complete product.
2. One improvement the team would make if development continued.

## 6. Instructor Questions During the Demo

The instructor may ask questions at any point.

Questions may address:

1. Saved-analysis persistence.
2. Save As semantics.
3. Q&A-history storage.
4. Re-ingestion behavior.
5. Duplicate detection.
6. Failed-refresh protection.
7. Evidence selection.
8. Review filtering.
9. Export generation.
10. Ownership and authorization.
11. Public deployment.
12. Architecture and implementation tradeoffs.
13. Code written or modified by a specific team member.

The team member responsible for the relevant area should normally answer.

**The demo clock continues while questions are being answered.**

## 7. Final Preparation Checklist

Before demo day, confirm all of the following:

- [ ] Public ReviewLens URL works.
- [ ] User A account works.
- [ ] User B account works.
- [ ] User A has at least two saved analyses.
- [ ] At least one analysis was created in an earlier session.
- [ ] Persisted Q&A history is available.
- [ ] Supporting evidence is available for a grounded answer.
- [ ] Complete review browsing works.
- [ ] Rating filter works.
- [ ] Date filter works when source dates are available.
- [ ] A safe analysis is prepared for Save As.
- [ ] A disposable analysis is prepared for deletion.
- [ ] An existing analysis is prepared for re-ingestion.
- [ ] Duplicate-prevention test evidence is identified.
- [ ] Failed-refresh preservation test evidence is identified.
- [ ] CSV export works.
- [ ] Markdown export works.
- [ ] Exported filenames are meaningful.
- [ ] A known User A resource is prepared for the User B isolation check.
- [ ] Representative Sprint 3 tests are identified.
- [ ] Latest successful CI run is easy to access.
- [ ] Demo browser tabs/tools are prepared.
- [ ] Team members know who will explain each area.
- [ ] The complete demonstration has been rehearsed within the 20-minute hard cap.
