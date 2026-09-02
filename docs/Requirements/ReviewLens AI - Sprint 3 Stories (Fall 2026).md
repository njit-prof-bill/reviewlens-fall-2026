# ReviewLens AI - Sprint 3 Stories (Fall 2026)

This is the Sprint 3 backlog for the ReviewLens AI capstone project.

Story writing format for Jira:

- Story ID
- Title
- Outcome — what must be true when complete
- Technical Guidance — implementation boundaries and expectations
- Rules — applicable canonical business rules

Sprint 3 focus: Production deployment, CI/CD automation, production configuration, application hardening, post-deployment verification, and completion of the production ReviewLens workflow.

Total stories: 20

Stories S3-001 through S3-004 establish the Sprint 3 deployment and reliability baseline and are primarily team-level engineering work.

Stories S3-005 through S3-020 define the primary application capabilities for Sprint 3. These 16 feature stories provide approximately three to four primary feature stories per developer for a five-person team.

## How To Read This Sprint Document

1. This file is the authoritative source for Sprint 3 scope.
2. `README.md` provides the overall product description, but Sprint 3 grading is based on this file.
3. Sprint 1 and Sprint 2 requirements remain in force unless explicitly changed here.
4. Sprint 3 represents the final production increment of the capstone.
5. Technical Guidance defines important implementation expectations but intentionally does not prescribe a specific hosting provider, cloud architecture, deployment platform, database technology, or CI/CD product unless explicitly stated.
6. Teams should make reasonable engineering decisions where implementation details are unspecified.
7. The objective of Sprint 3 is not merely to place the application on the internet. The deployed system must preserve the security, quality, and ReviewLens behavior developed during the first two sprints.

## Sprint 3 Demonstration Goal

The Sprint 3 application should demonstrate the complete production ReviewLens workflow:

1. A code change passes through the team's required CI quality gates.
2. An approved release is deployed through the team's automated deployment process.
3. Post-deployment verification confirms that the application is operational.
4. A user accesses the publicly deployed application.
5. The user authenticates.
6. The user creates or reopens an AnalysisTarget.
7. The user accesses real persisted review data or performs ingestion.
8. The user views the ingestion result summary.
9. The user asks an in-scope review question and receives a grounded response.
10. The user asks an out-of-scope question and ReviewLens declines it.
11. The team demonstrates that a different authenticated user cannot access the first user's data.
12. The team shows representative production health, smoke-test, and CI/CD evidence.

The team should demonstrate this as one coherent production application experience rather than as a collection of disconnected infrastructure features.

---

# CI/CD and Testing Requirements (Required)

All Sprint 1 and Sprint 2 CI/CD and testing requirements remain mandatory.

Sprint 3 adds deployment verification, smoke testing, migration verification, security scanning, and production reliability requirements.

## CI/CD Sprint 3 Ratchet

Every pull request must continue to run:

1. Lint or equivalent static checks.
2. Application build.
3. Automated unit tests.
4. Required integration tests.
5. Changed-code coverage gate.
6. Required AI orchestration and scope-guard tests.

Sprint 3 additionally requires:

7. Automated deployment from the team's protected release branch, normally `main` or equivalent.
8. Deployment must occur only after required quality gates pass.
9. Post-deployment health verification.
10. Automated smoke testing against the deployed application or production-equivalent environment.
11. Schema or migration verification when persistent-storage changes require it.
12. Dependency or security scanning appropriate to the selected technology stack.
13. Deployment or post-deployment failures must be visible in the pipeline.
14. A failed required deployment verification step must result in a failed release workflow rather than an apparently successful deployment.

## Test Baseline Expectations

1. Every feature story must include an appropriate automated test update.
2. Sprint 1 and Sprint 2 regression tests must continue to pass.
3. Production smoke tests should verify a small number of critical workflows rather than attempting to duplicate the complete automated test suite.
4. Smoke tests should be repeatable and safe to run against the deployed environment.
5. Production verification must not depend solely on a developer manually clicking through the application.
6. Production tests must preserve user isolation and must not expose real user data.
7. Environment-specific failures should be distinguishable from ordinary application failures where practical.
8. Security scanning should identify known dependency or configuration problems relevant to the team's technology stack.
9. Deployment tests should verify observable production behavior rather than merely verifying that a hosting command returned success.

## Minimum Test Evidence by Story Type

### Deployment

1. Required quality gates execute before deployment.
2. Passing release can deploy.
3. Failing required check prevents deployment.
4. Deployment result is visible.

### Production Health

1. Application endpoint is reachable.
2. Backend dependency or service health is verified where appropriate.
3. Failure produces a detectable non-success result.

### Smoke Testing

1. Authentication or protected access works.
2. User-owned ReviewLens data can be accessed.
3. Ingestion or persisted review access works.
4. Ingestion summary works.
5. Q&A works.
6. Scope guard still rejects an out-of-scope question.

### Security

1. Secrets are not stored in source control.
2. Production ownership rules remain enforced.
3. Cross-user access is denied.
4. Relevant dependency or configuration scanning runs automatically.

### Persistence and Migration

1. Required schema changes can be applied.
2. Application starts against the resulting schema.
3. Existing critical data remains usable after the change where applicable.

## Definition of Done Additions

A Sprint 3 story is not complete until:

1. The story outcome works in the deployed application when the behavior is production-facing.
2. Required automated tests pass locally where applicable.
3. Required automated tests pass in CI.
4. Sprint 1 and Sprint 2 regression tests continue to pass.
5. Deployment and post-deployment checks pass where applicable.
6. The story does not knowingly weaken authentication, authorization, ownership, ingestion, Q&A grounding, or scope-guard behavior established previously.
7. Production configuration does not expose protected secrets.
8. The pull request contains a short `Test Evidence` section.
9. Significant operational assumptions or limitations are documented.
10. Another team member can determine how to diagnose a failed release or production verification check.

---

# Canonical Business Rules (Sprint 3)

These rules are authoritative for Sprint 3 implementation and grading.

## S3-BR Production Deployment

1. **S3-BR-001**: The ReviewLens application must be deployed to a publicly reachable environment.
2. **S3-BR-002**: Protected ReviewLens functionality must continue to require authentication in production.
3. **S3-BR-003**: Production deployment must be initiated through the team's automated CI/CD process rather than requiring a developer to perform the normal release manually.
4. **S3-BR-004**: Deployment must occur only after required CI quality gates succeed.
5. **S3-BR-005**: A failing required quality gate must prevent the normal production deployment.
6. **S3-BR-006**: A deployment failure must be visible to the team.
7. **S3-BR-007**: A hosting provider reporting deployment success is not by itself sufficient evidence that the application is operational.

## S3-BR Production Configuration and Secrets

1. **S3-BR-008**: Production secrets must not be committed to source control.
2. **S3-BR-009**: Server-side credentials must not be exposed in browser-delivered application code.
3. **S3-BR-010**: Development, test, and production configuration must be separable without modifying application source code for every deployment.
4. **S3-BR-011**: Missing or invalid critical production configuration must produce a detectable failure.
5. **S3-BR-012**: Authentication provider, database, LLM provider, ingestion service, and other external-service credentials must follow the security mechanisms appropriate to the selected service.

## S3-BR Production Reliability

1. **S3-BR-013**: Failure of an external review source or ingestion service must not cause ReviewLens to silently fabricate successful ingestion.
2. **S3-BR-014**: Failure of the LLM service must produce an understandable application error rather than fabricated analysis.
3. **S3-BR-015**: User-visible production errors must not expose protected secrets or unnecessary sensitive internal details.
4. **S3-BR-016**: Existing valid persisted review data must not be silently destroyed because a later external operation fails.
5. **S3-BR-017**: Application logs should contain enough operational information to diagnose important failures without logging protected secrets.

## S3-BR Post-Deployment Verification

1. **S3-BR-018**: Every production deployment must be followed by an automated health verification.
2. **S3-BR-019**: Sprint 3 must include automated smoke tests of critical production behavior.
3. **S3-BR-020**: A failed required post-deployment verification must be visible as a failed release workflow or equivalent release failure.
4. **S3-BR-021**: Smoke tests should verify behavior against the deployed application rather than only retesting isolated local components.
5. **S3-BR-022**: Smoke tests must be designed so repeated execution does not corrupt production data.

## S3-BR Schema and Migration Safety

1. **S3-BR-023**: Persistent-storage schema changes required by a release must be represented in repeatable migration or schema-management artifacts where the selected technology requires them.
2. **S3-BR-024**: Required schema changes must be verified as part of the release process.
3. **S3-BR-025**: A release must not be considered successful if the deployed application is incompatible with the production persistence schema.

## S3-BR Security Verification

1. **S3-BR-026**: Production continues to enforce all Sprint 1 user-ownership and cross-user isolation rules.
2. **S3-BR-027**: Production Q&A continues to enforce all Sprint 2 active-dataset and cross-user AI-context rules.
3. **S3-BR-028**: The project must include automated dependency or security scanning appropriate to the team's selected technology stack.
4. **S3-BR-029**: Known security findings discovered by required scanning must be reviewed rather than ignored solely to make the pipeline green.
5. **S3-BR-030**: Teams should document accepted significant security findings when immediate remediation is not practical.

## S3-BR Production Application Lifecycle

1. **S3-BR-031**: A returning authenticated user must be able to reopen persisted AnalysisTargets created during an earlier session.
2. **S3-BR-032**: A user may delete only AnalysisTargets they own.
3. **S3-BR-033**: Deleting an AnalysisTarget must handle associated ReviewLens data consistently according to the team's documented persistence design.
4. **S3-BR-034**: If the team supports re-ingestion, the application must distinguish the result of the new ingestion attempt from earlier ingestion state sufficiently to avoid misleading the user.
5. **S3-BR-035**: Sophisticated historical comparison of ingestion datasets is not required.

## Rule Usage in Stories and Jira

1. Any Sprint 3 story may reference one or more S3-BR IDs instead of repeating the complete rule text.
2. Sprint 1 and Sprint 2 canonical business rules remain applicable where relevant.
3. If story behavior conflicts with a canonical business rule, the canonical business rule prevails.
4. A developer implementing a story is responsible for understanding all rules referenced by that story.

---

# A. Sprint 3 Deployment and Reliability Baseline

These are primarily team-level engineering stories.

## S3-001 - Add Automated Production Deployment

**Outcome:**  
An approved change merged through the team's protected release workflow automatically deploys ReviewLens to the team's production environment.

**Technical Guidance:**

The team may choose an appropriate hosting and deployment platform.

Examples include:

1. AWS.
2. Azure.
3. Google Cloud.
4. Vercel.
5. Netlify.
6. Render.
7. Railway.
8. Fly.io.
9. Supabase-hosted components.
10. Another instructor-approved platform.

The normal production deployment must be reproducible from committed repository configuration.

A developer should not need to:

1. Copy application files manually to a server.
2. Run an undocumented sequence of production commands from a laptop.
3. Change application source code to identify the production environment.

The pipeline should make it clear:

1. What commit is being deployed.
2. Whether deployment succeeded or failed.
3. Which environment received the deployment.

**Rules:** S3-BR-001 through S3-BR-007

## S3-002 - Add Post-Deployment Health Verification

**Outcome:**  
Every production deployment automatically verifies that the deployed ReviewLens application is reachable and operational.

**Technical Guidance:**

The health verification should test more than whether the deployment command completed.

At minimum, it should verify an application endpoint that demonstrates the deployed application can respond successfully.

Teams may implement:

1. Dedicated health endpoint.
2. Readiness endpoint.
3. Lightweight application request.
4. Equivalent production-health mechanism.

A useful health check may validate critical dependencies such as database connectivity, but teams should avoid making the health endpoint unnecessarily expensive or exposing sensitive details.

The health check must produce a non-success result when the deployed application is not operational.

**Rules:** S3-BR-007, S3-BR-018 through S3-BR-021

## S3-003 - Add Production Smoke Test Suite

**Outcome:**  
The deployment pipeline can run a small automated suite against the deployed ReviewLens environment to verify critical production behavior.

**Technical Guidance:**

The smoke suite should be deliberately smaller than the full automated test suite.

It should verify representative critical behavior such as:

1. Application availability.
2. Protected-route enforcement.
3. Access to a controlled user-owned AnalysisTarget.
4. Access to persisted review data or controlled ingestion behavior.
5. Ingestion summary.
6. Review Q&A.
7. Scope-guard behavior.

Teams may use a dedicated test account and controlled production test data.

The smoke tests must be safe to execute repeatedly.

Do not run destructive tests against arbitrary real user data.

**Rules:** S3-BR-018 through S3-BR-022, S3-BR-026, S3-BR-027

## S3-004 - Add Dependency and Security Scanning

**Outcome:**  
The CI pipeline automatically checks the project's dependencies or application artifacts for known security issues appropriate to the selected technology stack.

**Technical Guidance:**

Possible approaches include:

1. Package-manager vulnerability scanning.
2. GitHub dependency scanning.
3. Dependabot or equivalent.
4. Static application security analysis.
5. Container image scanning.
6. Secret scanning.
7. Equivalent platform-supported security tools.

Teams do not need to implement every category.

The selected checks should be meaningful for the actual project.

The team should be able to explain:

1. What is scanned.
2. When scanning runs.
3. What causes a build or release failure.
4. How significant findings are reviewed.

Simply enabling a scanner without reviewing its results does not satisfy the intent of the story.

**Rules:** S3-BR-028 through S3-BR-030

---

# B. Production Configuration and Failure Handling

## S3-005 - Configure Production Environment and Secrets

**Outcome:**  
The deployed ReviewLens application receives production configuration and protected credentials without embedding secrets in source control or browser-delivered code.

**Technical Guidance:**

The production environment may require configuration for:

1. Authentication provider.
2. Database.
3. LLM provider.
4. Review ingestion service.
5. Application URLs.
6. Logging or monitoring.
7. Other team-selected services.

The repository should document required configuration names without containing actual protected values.

Teams should understand the difference between:

1. Values intentionally safe for client-side use.
2. Server-side secrets that must remain protected.

A missing critical configuration value should produce a clear operational failure rather than unpredictable application behavior.

**Rules:** S3-BR-008 through S3-BR-012

## S3-006 - Separate Development, Test, and Production Configuration

**Outcome:**  
ReviewLens can run in development, automated testing, and production environments using environment-appropriate configuration without requiring source-code modification.

**Technical Guidance:**

For example:

- Development may use local services or developer credentials.
- Automated tests may use mocks or isolated test storage.
- Production uses protected hosted services.

The exact mechanism is team-defined.

Acceptable approaches include:

1. Environment variables.
2. Hosting-provider environment configuration.
3. Managed secret stores.
4. Configuration services.
5. Equivalent mechanisms.

Avoid logic such as manually editing source files before a production release.

Tests or startup validation should catch missing required configuration where practical.

**Rules:** S3-BR-008 through S3-BR-012

## S3-007 - Handle Review Ingestion Service Failure

**Outcome:**  
When the production review source, scraper, API, or ingestion dependency fails, ReviewLens reports the failure clearly without corrupting or fabricating review data.

**Technical Guidance:**

Representative failure cases may include:

1. Source unavailable.
2. Request timeout.
3. Rate limiting.
4. Changed source format.
5. Third-party API failure.
6. Authentication failure against an ingestion service.
7. Unexpected source response.

The exact failures depend on the team's ingestion architecture.

The application should:

1. Preserve previously valid persisted data.
2. Record the ingestion attempt as unsuccessful where appropriate.
3. Present useful user-facing failure information.
4. Log useful diagnostic information.
5. Avoid exposing secrets or raw credentials.

Automated tests should simulate at least one external ingestion failure.

**Rules:** S3-BR-013, S3-BR-015 through S3-BR-017

## S3-008 - Handle LLM Service Failure

**Outcome:**  
When the production LLM provider is unavailable or returns an unusable result, ReviewLens provides a meaningful failure state rather than fabricated analysis.

**Technical Guidance:**

Representative failures include:

1. Provider timeout.
2. Rate limit.
3. Provider authentication failure.
4. Service outage.
5. Invalid or malformed provider response.

The application should distinguish service failure from a legitimate ReviewLens refusal such as:

> The active reviews do not contain enough evidence to answer that question.

Those are different behaviors.

Tests should mock or simulate provider failure rather than relying on the provider actually becoming unavailable.

**Rules:** S3-BR-014 through S3-BR-017

---

# C. AnalysisTarget Production Lifecycle

## S3-009 - Reopen a Persisted AnalysisTarget

**Outcome:**  
A returning authenticated user can reopen an AnalysisTarget created during a previous session and access its persisted ReviewLens data.

**Technical Guidance:**

The user should be able to:

1. Authenticate in a later session.
2. View their existing AnalysisTargets.
3. Open a target.
4. View its ingestion state.
5. View its ingestion summary when data exists.
6. Continue using Q&A against its persisted review dataset.

The application should not require re-ingestion simply because the browser session ended.

Automated tests should verify persistence independently of transient frontend state.

**Rules:** S3-BR-031 and all applicable Sprint 1 and Sprint 2 ownership rules

## S3-010 - Delete an AnalysisTarget

**Outcome:**  
An authenticated user can delete an AnalysisTarget they own.

**Technical Guidance:**

The UI should make destructive intent clear.

The team must decide and document how associated data is handled.

Possible designs include:

1. Cascading deletion of reviews and ingestion records.
2. Soft deletion.
3. Another consistent persistence strategy.

The implementation should not leave data in a state that violates referential integrity or allows deleted targets to remain normally accessible.

Tests should verify:

1. Owner can delete the target.
2. Deleted target no longer appears in normal retrieval.
3. Associated data follows the documented deletion behavior.

**Rules:** S3-BR-032, S3-BR-033

## S3-011 - Prevent Cross-User Target Deletion

**Outcome:**  
An authenticated user cannot delete an AnalysisTarget owned by another user.

**Technical Guidance:**

This must be enforced by the backend or persistence authorization layer.

A frontend-hidden delete button is not sufficient.

The test should use two authenticated identities:

1. User A owns Target A.
2. User B submits a delete operation against Target A.
3. The operation is denied.
4. Target A and its associated data remain intact.

This story intentionally repeats the security principle established in Sprint 1 because destructive production operations deserve explicit verification.

**Rules:** S3-BR-026, S3-BR-032

## S3-012 - Re-Ingest an Existing AnalysisTarget

**Outcome:**  
If the team supports re-ingestion, a user can initiate another ingestion operation for an existing AnalysisTarget and distinguish the new result from the previous ingestion state.

**Technical Guidance:**

The team must define how re-ingestion affects existing reviews.

Possible strategies include:

1. Replace the current review dataset.
2. Merge newly collected reviews.
3. Preserve ingestion-run history.
4. Another documented strategy.

Sophisticated historical comparison is not required.

The important requirements are:

1. The behavior is explicit.
2. The user is not misled about which dataset is current.
3. A failed re-ingestion does not silently destroy a previously valid dataset.
4. Duplicate handling follows the team's documented strategy.

If a team deliberately does not support re-ingestion, the instructor may approve an equivalent production-lifecycle story.

**Rules:** S3-BR-013, S3-BR-016, S3-BR-034, S3-BR-035

---

# D. Deployment Safety and Persistence Verification

## S3-013 - Prevent Deployment When Required Quality Gates Fail

**Outcome:**  
A change that fails a required build, test, coverage, AI guardrail, integration, or security gate cannot proceed through the normal production deployment workflow.

**Technical Guidance:**

The team should be able to demonstrate this behavior safely.

For example:

1. Introduce or identify a deliberately failing test on a branch.
2. Show CI failure.
3. Show that the production deployment step is not executed.

The protected release workflow should enforce the dependency between verification and deployment.

Simply having separate test and deployment jobs that can run independently does not satisfy the requirement.

**Rules:** S3-BR-003 through S3-BR-005

## S3-014 - Surface Deployment Failure

**Outcome:**  
When the deployment platform reports a failed release, the CI/CD workflow clearly reports that failure to the team.

**Technical Guidance:**

The pipeline should not mark the overall release successful when the production deployment failed.

The team should be able to identify:

1. Which deployment failed.
2. Which commit was involved.
3. Which pipeline stage failed.
4. Where diagnostic information can be found.

Teams are not required to implement automated rollback unless they choose to do so.

The important requirement is accurate operational visibility.

**Rules:** S3-BR-006, S3-BR-007, S3-BR-020

## S3-015 - Verify Database Schema or Migration Compatibility

**Outcome:**  
When a release includes persistent-storage schema changes, the release process verifies that the production application and schema are compatible.

**Technical Guidance:**

The exact implementation depends heavily on the selected persistence technology.

For relational databases, this may involve:

1. Versioned migrations.
2. Migration execution during deployment.
3. Migration validation.

For managed or schema-flexible storage, the team should implement the equivalent verification appropriate to that platform.

The important requirements are:

1. Schema changes are repeatable.
2. The production release does not depend on an undocumented manual database edit.
3. Failure is visible.
4. The application is not reported healthy when it cannot operate against the resulting persistence structure.

If the team makes no Sprint 3 schema changes, it should still document the migration mechanism that would be used for future changes and demonstrate that the current schema is production compatible.

**Rules:** S3-BR-023 through S3-BR-025

---

# E. Production Verification and Complete ReviewLens Workflow

## S3-016 - Smoke Test Authentication and Protected Access

**Outcome:**  
Automated post-deployment verification confirms that the production application enforces authentication and protected access.

**Technical Guidance:**

The smoke test may verify a combination of:

1. Public landing page is reachable.
2. Protected endpoint rejects unauthenticated access.
3. Controlled authenticated test identity can access an authorized resource.

Teams should avoid making smoke tests dependent on manual MFA or other interactive authentication steps that cannot reasonably be automated.

The exact authentication test mechanism should be consistent with the managed identity provider's supported practices.

**Rules:** S3-BR-002, S3-BR-018 through S3-BR-022, S3-BR-026

## S3-017 - Smoke Test Review Data and Ingestion Summary

**Outcome:**  
Automated post-deployment verification confirms that production ReviewLens can access a controlled review dataset and produce its expected ingestion summary.

**Technical Guidance:**

The smoke test may use:

1. A dedicated production test target.
2. A controlled persisted fixture.
3. A safe repeatable ingestion source.
4. Another production-safe approach.

The test should verify at least:

1. Target can be accessed.
2. Review data exists or can be obtained.
3. Summary endpoint or workflow succeeds.
4. Summary contains plausible expected values.

Avoid depending on a third-party public site changing in a specific way during every deployment if a more deterministic production verification approach is available.

**Rules:** S3-BR-018 through S3-BR-022 and applicable Sprint 2 summary rules

## S3-018 - Smoke Test Review-Grounded Q&A

**Outcome:**  
Automated post-deployment verification confirms that the production ReviewLens Q&A path can successfully process an in-scope question against a controlled review dataset.

**Technical Guidance:**

The smoke test does not need to assert one exact natural-language answer.

It should verify behavior such as:

1. Request succeeds.
2. ReviewLens processes the intended AnalysisTarget.
3. Response is non-empty.
4. Response does not indicate an unexpected system failure.

If live-model variability makes semantic validation difficult, the team should choose a modest but defensible production assertion while relying on Sprint 2 deterministic tests for deeper behavior verification.

The smoke test should not replace the Sprint 2 Q&A test harness.

**Rules:** S3-BR-018 through S3-BR-022, S3-BR-027

## S3-019 - Smoke Test Production Scope Guard

**Outcome:**  
Automated post-deployment verification confirms that the deployed ReviewLens application still rejects a representative out-of-scope question.

**Technical Guidance:**

Use a stable representative question such as an unrelated general-knowledge request.

The test should verify the behavioral outcome rather than one exact sentence.

This test exists because production configuration, model changes, prompt deployment mistakes, or environment differences can break behavior that passed deterministic local tests.

A successful application deployment with a missing or incorrect system prompt is not a successful ReviewLens release.

**Rules:** S3-BR-018 through S3-BR-022, S3-BR-027 and applicable Sprint 2 scope-guard rules

## S3-020 - Verify Complete Multi-User Production Workflow

**Outcome:**  
The publicly deployed application supports the complete ReviewLens workflow while preserving authenticated user isolation.

**Technical Guidance:**

The team should demonstrate the deployed system with at least two distinct users.

A representative workflow is:

### User A

1. Authenticate.
2. Create or reopen an AnalysisTarget.
3. Ingest or access persisted reviews.
4. View the ingestion result summary.
5. Ask an in-scope review question.
6. Receive a grounded answer.
7. Ask an out-of-scope question.
8. Receive a ReviewLens scope refusal.
9. Log out.

### User B

1. Authenticate separately.
2. View only User B's AnalysisTargets.
3. Attempt to access User A's target or review resource.
4. Receive an authorization failure.
5. Ask Q&A against User B's own dataset without User A's review content entering the AI context.

This story is the final integration point for the capstone.

It does not replace the automated tests attached to the underlying stories. It demonstrates that those independently implemented capabilities function together as a production system.

**Rules:** S3-BR-001 through S3-BR-035 and all applicable Sprint 1 and Sprint 2 rules

---

# Sprint 3 Demo Expectations

The team has approximately 15 minutes to demonstrate the final ReviewLens increment.

The Sprint 3 demo should emphasize that ReviewLens has become a **production software system**, not merely that the team found a hosting provider.

A recommended demonstration flow is:

1. Show the production URL.
2. Briefly show the release pipeline and required quality gates.
3. Show that deployment occurs only after required checks pass.
4. Show the most recent successful deployment and post-deployment verification.
5. Authenticate into the deployed application as User A.
6. Reopen or create an AnalysisTarget.
7. Show persisted or newly ingested review data.
8. Show the ingestion result summary.
9. Ask an in-scope question and show a grounded response.
10. Ask an out-of-scope question and show the scope guard.
11. Log in as User B or otherwise demonstrate a second authenticated identity.
12. Demonstrate that User B cannot access User A's data.
13. Briefly show representative production smoke tests.
14. Briefly show security/dependency scanning.
15. Discuss one production failure mode and how the application handles it.

The team does not need to demonstrate every individual Jira story.

Every team member should be prepared to explain:

1. The stories they implemented.
2. The automated tests supporting those stories.
3. How their changes passed through CI.
4. How their work behaves in the production environment.
5. Important implementation or operational tradeoffs.
6. One thing they would improve if the product continued beyond the capstone.

---

# Sprint 3 Explicitly Out of Scope

The following functionality is not required for Sprint 3:

1. Multiple review platforms.
2. Enterprise-scale multi-region deployment.
3. Kubernetes.
4. Complex infrastructure solely for the purpose of demonstrating infrastructure complexity.
5. Automated horizontal scaling.
6. Full observability platforms with custom dashboards.
7. Automated rollback.
8. Blue/green deployment.
9. Canary deployment.
10. Disaster-recovery environments.
11. Multi-region database replication.
12. Enterprise Single Sign-On.
13. Team or organization accounts.
14. Administrator portals.
15. Sophisticated historical ingestion comparison.
16. Advanced analytics dashboards.
17. Long-term conversational memory.
18. Fine-tuned or custom-trained language models.

Teams may implement additional capabilities after all required Sprint 3 behavior is working, tested, deployed, and verified.

The objective is a **small production-quality system with disciplined engineering practices**, not an unnecessarily complex infrastructure project.