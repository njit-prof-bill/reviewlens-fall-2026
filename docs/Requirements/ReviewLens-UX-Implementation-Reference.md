# ReviewLens AI - UX Implementation Reference

## Purpose

This document is a textual companion to the supplied ReviewLens AI reference image.

The **reference image is the primary visual source of truth** for layout, hierarchy, density, spacing, visual tone, and interaction style. This document explains the intended behavior, page states, navigation model, and sprint-by-sprint implementation progression.

The goal is to build one coherent ReviewLens experience over three sprints rather than three separate interfaces.

---

## 1. Core UX Concept

ReviewLens should behave like a focused review-analysis workspace.

The primary user journey is:

**Create Analysis → Ingest Reviews → Review Summary → Ask Questions → Explore Evidence**

The application should feel closer to a research notebook or ChatGPT-style analysis workspace than to a traditional CRUD dashboard.

The visual reference establishes the desired tone:

- Clean
- Spacious
- Professional
- Minimal
- Modern SaaS
- Analysis-first
- Strong visual hierarchy
- Limited use of accent color
- Cards used to separate meaningful stages of analysis

Do not redesign the interface into a generic admin dashboard.

---

## 2. Global Layout

The application should use a two-part shell:

1. **Left navigation / analysis history panel**
2. **Main analysis workspace**

The main workspace may also include the narrow right-side **Current Analysis Scope** panel shown in the reference image when sufficient horizontal space is available.

On smaller screens, the right-side scope panel may collapse into the main content flow.

---

## 3. Left Analysis Panel

The left panel should behave similarly to the ChatGPT conversation sidebar.

Its purpose is to let the user:

- Start a new analysis
- Reopen a previous analysis
- Rename an analysis
- Save an analysis under a meaningful name
- Create a copy using Save As
- Delete an analysis
- See which analysis is currently active

Do **not** display the complete source URL as the primary label in the sidebar.

URLs are too long and difficult to distinguish quickly.

Each analysis should instead have a short human-readable name.

Examples:

- Blue Bottle Coffee - Mint Plaza
- Acme Wireless Headphones
- Downtown Hotel Reviews
- Restaurant A - Google Maps

### 3.1 New Analysis

A prominent **New Analysis** action should appear near the top of the sidebar or application header.

Selecting it opens a blank analysis workspace.

The user should not be forced through a wizard.

### 3.2 Analysis Naming

An analysis initially may receive a generated working name derived from the detected entity or source.

Examples:

- `Blue Bottle Coffee - Mint Plaza`
- `Untitled Analysis`

The user must be able to explicitly name or rename the analysis.

Support:

- **Save**
- **Save As**
- **Rename**
- **Delete**

A reasonable interaction is an overflow menu associated with the active analysis or sidebar item.

**Save** persists the current analysis under its current name.

**Save As** creates a new persisted analysis based on the current analysis and prompts for a new name.

**Rename** changes only the display name of the existing analysis.

**Delete** requires confirmation.

---

## 4. Main Workspace - Initial State

The initial state is intentionally simple.

When the user starts a new analysis, the page should primarily show:

1. A large URL input field
2. An **Analyze Reviews** button

The experience should resemble the top area of the reference image before any analysis results exist.

Suggested structure:

**Header**
- ReviewLens AI branding
- New Analysis action
- Optional lightweight Help / How It Works action

**Main content**
- URL input
- Analyze Reviews button

Do not display empty summary cards, empty Q&A cards, or placeholder charts before an analysis exists.

The page should feel intentionally sparse.

---

## 5. URL Input and Analyze Action

The URL input is the entry point to the analysis workflow.

The user pastes a supported review-platform URL.

Example:

`https://www.google.com/maps/place/...`

The primary button should be labeled:

**Analyze Reviews**

When selected:

1. Validate the URL.
2. Identify the source/platform.
3. Begin ingestion.
4. Show a clear processing state.
5. Populate the analysis workspace as results become available.

The application should not navigate the user to a completely different visual experience after analysis begins.

Instead, the current page should progressively become the analysis workspace shown in the reference image.

---

## 6. Progressive Analysis Workspace

Once analysis begins, the page should expand downward into a notebook-like sequence.

The reference image uses a numbered vertical progression.

This is a useful visual model and should be retained.

Conceptually:

1. Ingestion Summary
2. Review Preview
3. Question / Analysis
4. Additional Question / Analysis
5. Out-of-Scope Example
6. Ask Another Question

The exact numbering does not need to correspond to fixed business rules. The purpose is to visually communicate that the user is building an analysis over time.

---

## 7. Ingestion Summary

After successful ingestion, show an **Ingestion Summary** card near the top of the workspace.

The card should present high-value facts at a glance.

Recommended fields:

- Reviews collected
- Average rating
- Earliest review
- Latest review
- Platform
- Business / entity name
- Ingestion status

Use compact statistics rather than paragraphs.

The summary should visually communicate success, failure, or partial success.

Examples:

- Complete
- Failed
- Partial

Do not use the LLM to create these values. They come from persisted review data.

---

## 8. Current Analysis Scope

The right-side **Current Analysis Scope** card shown in the reference image is an important part of the design.

Its purpose is to remind the user exactly what ReviewLens is analyzing.

Recommended contents:

- Business / entity
- Platform
- Reviews analyzed
- Date range

Also include a short scope statement such as:

> This AI will answer questions only from this dataset.

This reinforces the product's core guardrail without forcing users to discover scope boundaries through failed questions.

The scope card should remain visible while the user scrolls when practical.

A sticky treatment is appropriate on desktop.

---

## 9. Review Preview

Below the ingestion summary, show a compact sample of the ingested review data.

The reference image uses a table-like preview.

Recommended columns:

- Rating
- Date
- Reviewer
- Review text

Only show a small sample initially.

Provide a **View more reviews** action if the team chooses to expose the larger dataset.

The preview exists to give the user confidence that:

1. Real reviews were ingested.
2. The dataset looks correct.
3. Q&A is operating on visible evidence.

Avoid turning the application into a large review-management table.

The reviews support the analysis experience; they are not the primary product surface.

---

## 10. Q&A Interaction Model

Q&A should appear below the review summary as part of the same analysis notebook.

Each user question should create a visible **Question** block.

Each ReviewLens response should appear directly below it as an **Analysis** block.

The visual relationship should be obvious:

**Question**

followed by

**Analysis**

Do not use generic alternating left/right chat bubbles.

The reference image's notebook/card model is preferred because it emphasizes analysis rather than casual conversation.

---

## 11. Analysis Responses

A grounded answer should contain:

1. Concise natural-language analysis
2. Optional highlighted themes or important phrases
3. Number of matching reviews when available
4. Confidence or evidence-strength indicator when supported
5. Supporting review excerpts

The user should be able to understand *why* ReviewLens produced the answer.

Supporting evidence is a key part of the visual design.

The reference image uses individual quotation cards beneath the analysis.

This is the preferred pattern.

Do not display enormous context dumps.

Show a small number of representative excerpts with an option to inspect more when useful.

---

## 12. Matching Reviews and Confidence

The reference image includes:

- Matching Reviews
- Confidence
- Number of matching reviews

These are desirable UI concepts, but they must reflect actual application behavior.

Do not fabricate numerical confidence merely to reproduce the mockup.

If the implementation has a defensible confidence or evidence-strength measure, show it.

If not, omit the numeric confidence indicator.

The same applies to "matching review" counts.

Only display values that the application can calculate reliably.

The visual design should follow the image, but correctness takes precedence over decorative metrics.

---

## 13. Insufficient Evidence

ReviewLens must visually distinguish a valid answer from a case where the reviews do not contain enough evidence.

Example:

> The available reviews do not contain enough information to determine whether customers consider the parking area safe at night.

This is not an application error.

It is a legitimate analysis result.

Use a calm informational treatment.

Do not use the same styling as:

- Scope refusal
- Provider failure
- Application error

---

## 14. Out-of-Scope Questions

The reference image shows a strong but restrained **Out of Scope** treatment.

Retain this pattern.

When a user asks something outside the active review dataset, show:

1. A clear Out of Scope heading
2. Short explanation
3. Reminder of the active scope

Example:

> I can only answer questions about reviews in the current dataset.

Avoid generic error language such as:

> Invalid request.

This is a product guardrail, not a system failure.

---

## 15. Ask Another Question

At the bottom of the current analysis, provide a persistent or easily discoverable question-entry control.

Suggested placeholder:

**Ask another question about these reviews...**

The input should clearly imply that questions are limited to the active review dataset.

The reference image also shows suggested prompts.

Suggested prompts are optional but useful.

Examples:

- What are the biggest complaints?
- What themes appear most frequently?
- What do customers like most?
- Is there feedback about prices?

Suggested questions must remain relevant to the active dataset.

---

## 16. Analysis Persistence

An analysis should be treated as a persistent user artifact.

It should preserve enough state that a user can reopen it later and continue working.

At minimum, persist:

- Analysis name
- Source URL
- AnalysisTarget identity
- Review dataset
- Ingestion summary
- Current analysis metadata

Q&A persistence is optional unless required by the active sprint.

If Q&A history is persisted, it must remain associated with the correct AnalysisTarget.

---

## 17. Switching Analyses

Selecting another saved analysis from the left sidebar should change the entire active workspace.

The new analysis should update:

- URL/source
- Ingestion summary
- Review preview
- Current Analysis Scope
- Q&A context
- Any visible historical questions belonging to that analysis

Do not allow state from one analysis to appear under another.

The active sidebar item should be visually distinct.

---

## 18. Loading States

Use deliberate loading states.

Examples:

- Validating URL...
- Collecting reviews...
- Preparing analysis...
- Asking ReviewLens...

Avoid indefinite generic spinners without explanatory text.

If ingestion or AI processing takes noticeable time, the user should understand what is happening.

Do not show technical implementation details.

---

## 19. Failure States

Failure UX should remain inside the same product experience.

### Invalid URL

Show a validation message near the URL input.

### Review Source Failure

Explain that ReviewLens could not collect reviews from the source.

If previously persisted data exists, preserve it.

### LLM Provider Failure

Explain that ReviewLens could not complete the analysis request.

Do not present this as "insufficient evidence."

### Authentication / Authorization Failure

Provide clear user-level guidance without exposing security internals.

Never show:

- Stack traces
- Raw exceptions
- Provider SDK errors
- Database messages
- Secret values

---

## 20. Visual Style

Follow the supplied reference image closely.

Key characteristics:

- White or very light background
- Thin gray borders
- Soft card separation
- Rounded corners
- Restrained shadows
- Purple primary accent
- Green success accents
- Orange warning / out-of-scope treatment
- Strong black/near-black typography
- Generous whitespace
- Compact but readable tables
- Clear hierarchy between labels, values, questions, and analysis

Do not overdecorate.

The interface should feel credible as a modern SaaS analysis product.

---

## 21. Responsive Behavior

Desktop is the primary design target.

On smaller screens:

1. Collapse the left analysis panel into a drawer or menu.
2. Move the Current Analysis Scope card into the main content flow.
3. Stack summary metrics vertically or into multiple rows.
4. Allow review-preview tables to become card/list views if necessary.
5. Keep question and analysis blocks readable.
6. Preserve active AnalysisTarget context.

Do not attempt to preserve a wide desktop layout by forcing horizontal scrolling across the entire page.

---

## 22. Sprint-by-Sprint UX Delivery

The final UX should emerge progressively across the three sprints.

Do not build the entire reference image in Sprint 1.

### Sprint 1 - Analysis Foundation

Sprint 1 should establish the application shell and the ingestion workflow.

Primary UX:

#### Application Shell

- ReviewLens branding
- Left analysis sidebar
- New Analysis action
- Active analysis selection
- Basic Save / Save As / Rename / Delete behavior where supported
- Authentication and protected application experience

#### New Analysis State

- URL input
- Analyze Reviews button
- Validation states
- Processing state

#### AnalysisTarget Workspace

After ingestion:

- Active entity/source identification
- Ingestion state
- Basic review preview
- Persisted AnalysisTarget
- Ability to reopen an analysis

#### Sprint 1 UX Goal

The user should be able to:

**Start a new analysis → provide a review URL → ingest reviews → see that the analysis was saved and review data exists.**

The Q&A notebook does not need to exist yet.

### Sprint 2 - Review Intelligence

Sprint 2 builds the central experience shown in the reference image.

Add:

#### Ingestion Summary

- Review count
- Rating summary
- Date range
- Platform
- Entity
- Rejected/skipped record information when applicable

#### Current Analysis Scope

Add the right-side scope panel or responsive equivalent.

#### Q&A Notebook

Add:

- Question blocks
- Analysis blocks
- Supporting evidence
- Matching-review information when reliable
- Suggested follow-up questions

#### Guardrail States

Add distinct treatments for:

- Grounded answer
- Insufficient evidence
- Out-of-scope question
- AI/provider failure

#### Target Switching

Switching analyses must update:

- Summary
- Scope
- Review data
- Q&A context

#### Sprint 2 UX Goal

The user should be able to:

**Open an analysis → understand the dataset → ask grounded questions → inspect supporting evidence → see ReviewLens reject unsupported or out-of-scope requests.**

This sprint should visually approach the supplied reference image most closely.

### Sprint 3 - Production Experience

Sprint 3 completes and hardens the user experience.

Primary additions:

#### Production Persistence

- Returning users can reopen prior analyses
- Analysis naming remains stable
- Persisted review data remains available
- Production URL provides the same coherent UX

#### Analysis Lifecycle

- Delete owned analyses safely
- Re-ingestion or approved equivalent lifecycle behavior
- Clear distinction between current and prior ingestion state when applicable

#### Production Failure Handling

Polish:

- External review-source failure
- LLM-provider failure
- Missing configuration
- Session expiration
- Other production-safe recovery states

#### Production Polish

Ensure:

- No developer/debug UI leaks into production
- Loading states are coherent
- Error states are user-facing
- Responsive behavior is complete
- Navigation and analysis context remain consistent
- Publicly deployed application matches the intended product experience

#### Sprint 3 UX Goal

The user should experience ReviewLens as a **complete production application**, not as a class project running on a developer machine.

---

## 23. What Not To Build

Do not add complexity that is not required by the product.

Avoid:

- Generic admin dashboards
- Large settings areas without purpose
- Multi-pane enterprise analytics dashboards
- General-purpose AI chat
- Complex visualizations simply for appearance
- Multiple competing navigation systems
- Separate disconnected ingestion, review, and Q&A applications
- Dense developer-oriented diagnostic screens
- Elaborate animation that slows normal use

The design should remain focused on the analysis workflow.

---

## 24. UX Success Criteria

The finished product should satisfy three qualities.

### Consistency

Repeated actions, controls, and states behave the same way throughout the product.

### Clarity

At all times, the user can understand:

- Which analysis is active
- Which entity is being analyzed
- Which dataset is in scope
- What ReviewLens just did
- Whether the answer is grounded, unsupported, out of scope, or failed

### Flow

The user can naturally move through:

**New Analysis → Ingestion → Summary → Review Evidence → Q&A → Continued Exploration**

without losing context.

The supplied reference image is the target visual language for this experience.
