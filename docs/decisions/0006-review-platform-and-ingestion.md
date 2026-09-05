# 0006 - Review Platform and Ingestion Approach

Date: 2026-09-04
Status: Accepted

## Context

Sprint 1 requires ReviewLens to support exactly one public review platform
(S1-BR-012) and to obtain real review data from an AnalysisTarget's source
(S1-020). The UX reference specifies a URL field and an **Analyze Reviews**
button, so ingestion must be URL-driven rather than a file-upload workflow.

Google Maps is the platform, matching the wireframe. Collecting its reviews is
the hard part:

- The Google Places API returns roughly five reviews per place, short of the
  15-20+ the demo requires.
- Direct scraping faces consent interstitials, infinite scroll, and active bot
  detection, and is brittle enough to fail during a timed demonstration.

## Decision

**Platform:** Google Maps, exclusively.

**Primary ingestion path:** URL-driven collection through a third-party
review-data provider. The default implementation targets SerpApi's
`google_maps_reviews` engine. The place identifier is extracted from the
supplied Maps URL, short links are expanded first, and pages are followed up to
`REVIEW_FETCH_MAX`.

**Recovery path:** CSV/JSON file import, exposed as a subordinate action in the
workspace and surfaced prominently only after a provider failure. It exists
because the demo script requires a fallback when the live source is unavailable.
A team that implemented only import would not satisfy S1-020.

**Provider abstraction:** Both paths implement the `ReviewSource` protocol in
`app/services/ingestion/base.py` and share one normalizer, so the persisted
`Review` shape is provider-independent and a different vendor or a self-hosted
scraper can be substituted without touching persistence, routing, or the UI.

## Consequences

**Positive**

- The wireframe's Analyze Reviews action is literally true.
- Review volume is sufficient for meaningful Sprint 2 analysis.
- Provider failure modes are explicit and testable: timeout, unavailable, quota
  exceeded, place not found, no reviews available.
- Tests replay a recorded provider response, so CI never touches the network.

**Negative**

- A paid third-party account is a hard prerequisite, not an optional extra.
- Quota is a real operational limit during development and demos.
- `REVIEW_PROVIDER_API_KEY` must be handled as a server-side secret.
- Collection latency makes ingestion asynchronous, which adds the run-status
  polling machinery the UI depends on.

**Neutral**

- Ingestion is asynchronous: `POST /analysis-targets/{id}/ingestions` returns
  202 with an `IngestionRun`, and the client polls until a terminal status.

## Alternatives considered

**Self-hosted Playwright scraper.** No vendor cost, but brittle against Google's
protections and a poor risk during a 20-minute demo with a hard time cap.

**Google Places API.** Officially supported and cheap, but the review cap makes
the dataset too small for the sprint requirements.

**Import-only.** Permitted by an earlier reading of S1-BR-019 and the lowest
risk, but it contradicts the UX reference and leaves the Analyze Reviews button
meaningless.

**A more scrapable platform** (Steam, Trustpilot, app stores). Would remove the
vendor dependency, but Google Maps is what the wireframe and product brief
describe.
