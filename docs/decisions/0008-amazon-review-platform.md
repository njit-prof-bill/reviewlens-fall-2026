# 0008 - Add Amazon as a Review Source

Date: 2026-09-26
Status: Accepted

## Context

The initial ReviewLens implementation supports Google Maps only (decision
0006). The product now needs Amazon product reviews as an additional public
source while preserving the existing one-source-per-AnalysisTarget boundary.
The capstone Sprint 1 requirement describes one platform per team, so adding a
second platform to capstone delivery requires instructor approval; otherwise
this is a post-capstone extension.

## Decision

- Accept Google Maps place URLs and Amazon.com product URLs containing an ASIN.
  Initially reject Amazon search, storefront, regional-marketplace, and
  unsupported URLs.
- Detect the platform from one URL field. Store one platform and source URL per
  AnalysisTarget; Google and Amazon reviews are separate analyses and are never
  merged implicitly.
- Collect Amazon reviews using SerpApi's `amazon_product` engine and persist
  only individual `reviews_information.authors_reviews` entries. Do not ingest
  provider-generated summaries as Review records.
- Dispatch URL ingestion by the persisted platform and normalize both sources
  into the existing Review shape. Continue target-scoped refresh and
  deduplication. Use an Amazon product title to replace only the generated ASIN
  placeholder, not a user-selected analysis name.
- Configure provider order using `REVIEW_PROVIDER` and optional comma-separated
  `REVIEW_PROVIDER_FALLBACKS`. Fail over only on timeout, provider unavailability,
  or quota errors. Do not fail over for invalid products or empty review sets,
  and do not merge partial records across providers within one run.
- Keep the new-analysis form to one generically labeled URL field, with source
  guidance below it and an arrow-only submit button with an accessible name and
  tooltip. Show platform labels on saved analyses and source-specific entity
  labels in scope.

## Consequences

**Positive**

- Teams can analyze Google Maps businesses and Amazon products using the same
  saved-analysis workspace and Q&A scope guardrails.
- Provider selection is separated from endpoint routing, and transient provider
  failures can use an explicitly ordered fallback when another adapter is
  registered and its review identities are compatible.
- The UI reports the real number of individual records collected; it never
  turns aggregate summaries into fabricated reviews.

**Negative / open limitations**

- The documented Amazon Product API response contains authored reviews, but its
  public documentation does not establish review pagination or a minimum number
  of records. Collection is limited to the individual records returned in that
  response, and a live-provider smoke test is still required before relying on
  dataset size for a demo.
- The documented authored-review schema does not include a stable review ID or
  review URL. ReviewLens therefore uses its deterministic content fingerprint
  for deduplication; changes to a review's stable fingerprint fields may be
  treated as a new record.
- SerpApi is currently the only registered provider adapter. A fallback vendor
  needs its own implementation, credentials, cost and terms review, stable
  review-identity validation, and recorded-response tests before it can be
  configured.
- No live Amazon request was validated during implementation because a provider
  key was not available.
- The platform expansion exceeds the Sprint 1 one-platform statement unless the
  instructor approves the capstone scope.

## Verification

Tests use a redacted-shape local fixture and do not contact SerpApi. Before a
capstone or public demo, verify a real `amazon.com` product URL and confirm the
provider returns enough individual review records, stable identities, and
permitted persistence under the selected account and terms.
