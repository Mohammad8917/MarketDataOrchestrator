# Compliance Registry

Architecture Frozen v1.0 — authoritative Compliance Matrix and Exception Registry.

This document is the canonical physical location for the Compliance Matrix and Exception Registry defined by Clause 24.12.3.

## Compliance Matrix

Every mandatory control is represented by exactly one stable control ID.

### Canonical control record schema

```yaml
control_id: "<stable-id>"
rule: "<normative requirement>"
severity: "BLOCKING|NON_BLOCKING"
owner: "<role-or-owner>"
artifact: "<path-or-artifact>"
applicability: "ALWAYS|CONDITIONAL|NA"
verification: "<mechanical-check-or-review>"
ci_gate: "<named-gate>"
evidence: "<reference>"
evidence_timestamp: "<UTC>"
evidence_input_fingerprint: "<hash-or-equivalent>"
status: "PASS|FAIL|NOT_VERIFIED|NA"
exception_id: null
```

### Control baseline

| control_id | artifact | owner | ci_gate | status |
|---|---|---|---|---|
| C01_FILE_HEADER | repository Python source files | architecture | G04_ARCHITECTURE_DEPENDENCY | NOT_VERIFIED |
| C02_FILE_VERSION | repository Python source files | architecture | G04_ARCHITECTURE_DEPENDENCY | NOT_VERIFIED |
| C03_OWNERSHIP_DEPENDENCIES | repository source files | architecture | G04_ARCHITECTURE_DEPENDENCY | NOT_VERIFIED |
| C04_ASYNC_SECURITY | ingestion/providers | security | G07_INTEGRATION_RESILIENCE | NOT_VERIFIED |
| C05_CONTRACT_REGISTRY | docs/contracts.md | architecture | G03_UNIT_CONTRACT | NOT_VERIFIED |
| C06_PROVIDER_CAPABILITY | docs/capability-matrix.md | ingestion | G06_SECURITY_SUPPLY_CHAIN | NOT_VERIFIED |
| C07_RATE_LIMIT_REGISTRY | docs/capability-matrix.md | ingestion | G07_INTEGRATION_RESILIENCE | NOT_VERIFIED |
| C08_COMPLIANCE_MATRIX | docs/README.md | architecture | G04_ARCHITECTURE_DEPENDENCY | NOT_VERIFIED |
| C09_EXCEPTION_REGISTRY | docs/README.md | architecture | G04_ARCHITECTURE_DEPENDENCY | NOT_VERIFIED |
| C10_TEMPORAL_INTEGRITY | temporal boundaries | architecture | G07_INTEGRATION_RESILIENCE | NOT_VERIFIED |
| C11_PROVENANCE | evidence | evidence | G08_RELEASE_VERIFICATION | NOT_VERIFIED |
| C12_COVERAGE | testable production Python | quality | G05_COVERAGE | NOT_VERIFIED |
| C13_SECURITY_SUPPLY_CHAIN | dependency/build/security artifacts | security | G06_SECURITY_SUPPLY_CHAIN | NOT_VERIFIED |
| C14_RELEASE_PROVENANCE | evidence/RELEASE_PROVENANCE.json | release | G08_RELEASE_VERIFICATION | NOT_VERIFIED |
| C15_RESOURCE_BUDGETS | production-critical components | operations | G07_INTEGRATION_RESILIENCE | NOT_VERIFIED |
| C16_BACKUP_RECOVERY | stateful/availability-critical components | operations | G07_INTEGRATION_RESILIENCE | NOT_VERIFIED |
| C17_RUNBOOKS | operational control plane | operations | G07_INTEGRATION_RESILIENCE | NOT_VERIFIED |
| C18_ADR_DECISIONS | architecture decision records | architecture | G04_ARCHITECTURE_DEPENDENCY | NOT_VERIFIED |
| C19_INCIDENT_CONTROLS | incident records | operations | G07_INTEGRATION_RESILIENCE | NOT_VERIFIED |
| C20_REPRODUCIBLE_RELEASE | release artifacts | release | G08_RELEASE_VERIFICATION | NOT_VERIFIED |

### Normative Appendix control IDs

| appendix | control_id | ci_gate |
|---|---|---|
| A | APP-A-01 | G06_SECURITY_SUPPLY_CHAIN |
| A | APP-A-02 | G06_SECURITY_SUPPLY_CHAIN |
| A | APP-A-03 | G06_SECURITY_SUPPLY_CHAIN |
| A | APP-A-04 | G06_SECURITY_SUPPLY_CHAIN |
| A | APP-A-05 | G06_SECURITY_SUPPLY_CHAIN |
| A | APP-A-06 | G06_SECURITY_SUPPLY_CHAIN |
| A | APP-A-07 | G06_SECURITY_SUPPLY_CHAIN |
| A | APP-A-08 | G06_SECURITY_SUPPLY_CHAIN |
| B | APP-B-01 | G08_RELEASE_VERIFICATION |
| B | APP-B-02 | G08_RELEASE_VERIFICATION |
| B | APP-B-03 | G08_RELEASE_VERIFICATION |
| B | APP-B-04 | G08_RELEASE_VERIFICATION |
| B | APP-B-05 | G08_RELEASE_VERIFICATION |
| C | APP-C-01 | G06_SECURITY_SUPPLY_CHAIN |
| C | APP-C-02 | G06_SECURITY_SUPPLY_CHAIN |
| D | APP-D-01 | G07_INTEGRATION_RESILIENCE |
| E | APP-E-01 | G07_INTEGRATION_RESILIENCE |
| F | APP-F-01 | G07_INTEGRATION_RESILIENCE |
| G | APP-G-01 | G07_INTEGRATION_RESILIENCE |
| H | APP-H-01 | G04_ARCHITECTURE_DEPENDENCY |
| I | APP-I-01 | G07_INTEGRATION_RESILIENCE |
| J | APP-J-01 | G08_RELEASE_VERIFICATION |

## Mandatory CI gates

| gate | required purpose | status |
|---|---|---|
| G01_FORMAT_LINT | formatting and lint validation | NOT_VERIFIED |
| G02_TYPECHECK | static type validation | NOT_VERIFIED |
| G03_UNIT_CONTRACT | unit and contract verification | NOT_VERIFIED |
| G04_ARCHITECTURE_DEPENDENCY | ownership and dependency-direction validation | NOT_VERIFIED |
| G05_COVERAGE | 100% statement + branch acceptance for applicable production Python | NOT_VERIFIED |
| G06_SECURITY_SUPPLY_CHAIN | security, SCA, secrets, license, SBOM and supply-chain controls | NOT_VERIFIED |
| G07_INTEGRATION_RESILIENCE | integration, temporal, concurrency, resource and resilience controls | NOT_VERIFIED |
| G08_RELEASE_VERIFICATION | artifact identity, provenance and release verification | NOT_VERIFIED |

A NOT_VERIFIED status is deliberate until executable evidence exists. It is never equivalent to PASS.

## Exception Registry

Each exception MUST have an exact control binding, scope, owner, approval, expiry, compensating control and remediation.

```yaml
exception_id: "<unique-id>"
rule_or_control: "<control-id>"
owner: "<accountable-owner>"
scope: "<exact-files-artifacts-environments>"
reason: "<documented-reason>"
compensating_control: "<required-control>"
created_at: "<UTC>"
expires_at: "<UTC>"
approver: "<authorized-approver>"
status: "ACTIVE|EXPIRED|REVOKED"
remediation: "<follow-up>"
```

No active exception is declared by this baseline. An absent exception record means no exception is granted.
