# Security Findings

## Automated Checks

The `security-checks` CI job runs Gitleaks, `npm audit --audit-level=high`, and
`pip-audit --strict`. Dependabot checks npm and pip dependencies weekly.

Any actionable finding fails CI. Do not disable a scanner or lower its threshold
only to make a workflow green.

## Review Process

1. Identify the advisory, affected dependency, severity, and reachable use.
2. Upgrade or remove the dependency when practical.
3. If remediation cannot happen immediately, record the finding below with an
   owner, reason, compensating control, and review date.
4. Revisit documented findings after every Dependabot update or before release.

## Accepted Findings

None at Sprint 3 start.
