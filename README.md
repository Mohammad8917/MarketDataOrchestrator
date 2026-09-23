# MarketDataOrchestrator — Architecture & Implementation Compliance Kit

**Architecture:** Frozen v1.0  
**Runtime:** Python 3.13+  
**Project:** Layered, event-driven market-data and analysis orchestrator for Crypto, Forex, and Gold  
**Owner / Author:** محمد حسن زاده  
**License policy:** Proprietary — All Rights Reserved

This README is the authoritative **Architecture & Implementation Compliance Kit** for the repository. The physical repository tree, layer boundaries, contracts, temporal rules, provenance, security controls, testing gates, and review gates defined here are mandatory.

The frozen architecture is authoritative. Code must adapt to the architecture; the architecture must not be silently changed to accommodate code.

---

## MANDATORY KIT ENTRY GATE

Every entry into this Compliance Kit MUST begin with:

**ENTER KIT → CHECK COMPLIANCE KIT → VERIFY REQUEST AGAINST KIT → ONLY THEN PROCEED**

Before analysis, design, code generation, file modification, commit, release, or repository change:

1. Read the current Compliance Kit.
2. Identify the requested change, its scope, and its non-goals.
3. Verify the request against the frozen tree, ownership boundaries, contracts, dependency direction, security requirements, temporal/provenance rules, and acceptance gates.
4. Verify that the required provider/library capabilities actually exist.
5. Only then proceed.

This check is repeated on every new entry into the Kit. A previous check does not authorize a later, materially different change.

If a request conflicts with a mandatory rule, implementation MUST stop at the conflict and the conflict MUST be resolved through the documented architecture/contract-change process.

---

## Architecture invariants

- The repository tree is frozen at Architecture v1.0 unless explicitly unfrozen through an architecture change.
- One implementation file has one primary responsibility.
- Dependencies are explicit, directional, and minimal.
- Cross-layer communication occurs through declared contracts.
- Concrete providers must not leak into prohibited upper layers.
- External data remains traceable to its source.
- Time semantics are explicit and UTC-based at system boundaries.
- Provider failures are isolated.
- Secrets never enter source, logs, fixtures, telemetry, or commits.
- Production readiness requires automated verification, not merely code existence.
- No rule in this README authorizes bypassing another mandatory rule.

### Rule precedence

When requirements appear to conflict, apply this order:

1. Security, privacy, and legal constraints.
2. Frozen architecture and ownership boundaries.
3. Contract definitions and Contract Evolution Policy.
4. Data integrity, temporal integrity, and provenance requirements.
5. Testing and verification gates.
6. Provider capability and operational constraints.
7. Coding/style modernization.

A lower-priority rule MUST NOT be used to bypass a higher-priority rule.

---

# 1. Mandatory source-file header

Every newly created or materially modified source file MUST contain a machine-readable compliance header appropriate to its file type.

For Python source files, the header MUST be a valid module docstring and MUST appear before executable code. It MUST identify:

- file path/name;
- repository/Kit reference;
- file SemVer;
- last material-change date in both Persian-calendar and Gregorian form;
- author/owner;
- exactly one primary responsibility;
- architectural layer/subsystem;
- direct runtime dependencies;
- dependency versions or the authoritative lock/manifest reference from which versions are resolved;
- Python compatibility: 3.13+;
- proprietary/all-rights-reserved notice;
- unauthorized-use warning;
- compliance-kit reference.

### 1.1 Canonical machine-readable header schema

The logical header schema is fixed and MUST be machine-parseable. The canonical field order is exactly:

`FILE, KIT, FILE_VERSION, DATE_GREGORIAN, DATE_PERSIAN, AUTHOR, RESPONSIBILITY, LAYER, OWNS, DOES_NOT_OWN, DEPENDENCIES, PYTHON, LICENSE, NOTICE, COMPLIANCE`

For Python, the canonical representation is one `KEY: VALUE` record per line inside the module docstring. The key order above MUST NOT change. Values MUST be UTF-8, single-line, and non-empty unless the applicable value is explicitly `N/A`. List-valued fields MUST use semicolon-separated items. The parser MUST split only on the first colon so values may contain additional colons. Duplicate keys, unknown keys, missing keys, reordered keys, malformed records, or parser errors are compliance failures.

Canonical example:

```text
"""
FILE: validation/example.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: <exactly one primary responsibility>
LAYER: <frozen architectural layer/subsystem>
OWNS: <owned behavior/state/contracts>
DOES_NOT_OWN: <delegated behavior/state>
DEPENDENCIES: dependency_a; dependency_b
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""
```

For non-Python files, the same fifteen logical keys and exact order MUST be represented using the file's native comment/metadata syntax. Generated files MAY use native generator metadata only when comments are invalid, but the same canonical fields MUST remain auditable. A compliance validator MUST verify field count, key order, uniqueness, syntax, required-value presence, and agreement with repository facts. Header parser failure or unverifiable header evidence MUST result in **NOT VERIFIED**.

The header is documentation, not the authoritative dependency resolver. Dependency truth MUST also be maintained in the project's dependency/lock configuration.

For non-Python files, use the native comment/documentation syntax. Generated files MAY use the generator's native metadata mechanism when comments are not valid, but the same information MUST remain auditable.

Headers MUST be updated when their declared facts materially change. Header-only edits do not establish architectural compliance.

---

# 2. Unauthorized-use notice

Source and proprietary project artifacts MAY contain an unauthorized-use notice stating that copying, redistribution, modification, reverse engineering, sale, or other use without written authorization is prohibited.

The notice is a project legal notice and MUST NOT claim guaranteed legal remedies or substitute for legal advice.

Applicable rights, restrictions, exceptions, and remedies depend on governing law and the facts.

Owner: **محمد حسن زاده**.

---

# 3. Version and date

Every newly created or materially modified source file MUST carry:

- a file-level SemVer;
- the Gregorian date of the material change;
- the Persian-calendar date of the material change.

Repository release versioning is separate and MUST be governed by the project's authoritative release metadata, such as VERSION/pyproject metadata, CHANGELOG, and Git tags where present.

A file-version change MUST describe a material change to that file. Cosmetic edits alone MUST NOT be used to manufacture a version transition.

---

# 4. Python compatibility

Production Python MUST target **Python 3.13+**.

Rules:

- Runtime compatibility MUST be verified by CI.
- The supported interpreter range MUST be declared in the authoritative project metadata. The current repository declaration is `requires-python = ">=3.13"` in `pyproject.toml`.
- Type checking and linting MUST run against the declared target.
- Deprecated APIs MUST NOT be introduced without a documented compatibility decision.
- APIs removed before Python 3.13 MUST NOT be used.
- Version-specific behavior MUST be covered by tests when it affects project behavior.
- "Python 3.13+" means the minimum supported version is 3.13; it does not authorize syntax or APIs unavailable on the declared minimum version.

---

# 5. Architecture ownership and dependencies

Every implementation file MUST declare:

1. exactly one primary responsibility;
2. its architectural layer/subsystem;
3. its actual direct runtime dependencies;
4. important dependency-direction constraints;
5. what it OWNS;
6. what it explicitly DOES NOT OWN.

Rules:

- Direct dependency means an implementation dependency used by the file at runtime or required to construct its declared behavior.
- Architectural permission is not a direct dependency.
- Transitive dependencies MUST NOT be listed as direct dependencies unless the file directly uses them.
- Dependencies MUST point only through allowed architectural boundaries.
- A lower layer MUST NOT import an upper layer.
- Concrete provider implementations MUST NOT become dependencies of domain/analysis/decision/risk code when a contract/interface is defined.
- Circular dependencies are forbidden unless explicitly proven to be type-checking-only and isolated with a sanctioned mechanism.
- Hidden imports, dynamic global registries, and side-effect imports MUST NOT be used to bypass dependency ownership.
- Dependency direction MUST be testable.

---

# 6. Async-first and security requirements

For exchange/network integrations:

- Async I/O is mandatory for network operations.
- Blocking I/O MUST NOT execute on the event loop.
- Blocking libraries, if unavoidable, MUST be isolated behind an explicit executor/thread boundary with bounded concurrency.
- Every external call MUST have an explicit timeout.
- Retries MUST be bounded.
- HTTP 429 and equivalent provider rate-limit signals MUST be handled explicitly.
- Backoff MUST use exponential growth with jitter and a hard maximum.
- Secrets MUST come from approved environment/secret-management infrastructure.
- Secrets MUST NOT be committed, logged, embedded in fixtures, included in exceptions, telemetry, URLs, or serialized application state.
- Credentials MUST only be sent to the intended provider endpoint and only as required by the provider contract.
- Provider connectors MUST be isolated behind shared contracts.
- Error messages MUST contain enough context for diagnosis without exposing sensitive values.

---

# 7. Exchange integration target

The project targets integration capability for at least:

1. Binance
2. Coinbase
3. Kraken
4. KuCoin
5. OKX
6. Bybit
7. Gate.io
8. HTX (Huobi)
9. Bitfinex
10. Bitstamp
11. MEXC
12. Crypto.com
13. Bitget
14. Gemini
15. Upbit

This is a **capability target**, not a claim that every provider currently exposes identical REST, WebSocket, testnet, symbol, order, or market-data functionality.

Before implementation or release, each provider capability MUST be verified against current official provider documentation.

For each provider, the repository MUST distinguish at minimum:

- REST availability;
- WebSocket availability;
- authentication requirements;
- test/sandbox availability, if any;
- supported market-data capabilities;
- supported trading capabilities, if in scope;
- symbol/instrument constraints;
- rate limits;
- relevant provider contract version.

Unsupported provider capabilities MUST NOT be represented as implemented.

Exchange-specific details MUST remain inside the provider/adapter boundary and MUST NOT leak into domain, analysis, decision, risk, or other prohibited layers.

---

# 8. Testing and quality gates

Production implementation MUST satisfy:

- complete type annotations for public APIs and meaningful internal boundaries;
- documentation for public classes/functions/methods;
- Ruff-compatible linting;
- mypy-compatible static typing;
- pytest;
- pytest-asyncio where async behavior exists;
- mocked external calls in unit tests;
- architecture/dependency tests;
- contract tests;
- integration/E2E tests where the behavior cannot be established by unit tests;
- CI verification before merge/release.
- Security scanning MUST include static analysis, dependency/SCA scanning, secret scanning, and license/compliance checks where applicable.
- Dependency versions MUST resolve from an authoritative lock/constraints mechanism; production dependencies MUST be reproducible and integrity-verified.
- Dependency changes MUST be reviewed for vulnerability, license, provenance, and transitive-impact risk.
- An SBOM MUST be producible for every releasable artifact, with component versions and dependency relationships.
- CI MUST enforce the mandatory order: formatting/lint → type-check → unit/contract tests → architecture/dependency tests → coverage → security/dependency/license checks → integration/E2E/resilience checks where applicable → release verification.
- A failed mandatory gate MUST block merge/release; local overrides MUST NOT weaken the repository gate.
- Critical security findings, known-exploitable dependencies, leaked secrets, or unresolved contract/architecture violations MUST block release unless an explicitly documented exception is approved under the change-control process.

Per-file statement and branch coverage is a **100% acceptance gate** for testable production Python files, as defined in clause 11.

Aggregate coverage MAY be reported separately but MUST NOT conceal a failing per-file gate.

---

# 9. Review workflow

Every production change follows:

**DRAFT → SELF-REVIEW → PEER-REVIEW → APPROVED → RELEASED**

Required review evidence includes, as applicable:

- changed files;
- responsibility/dependency verification;
- contract impact;
- architecture/dependency-direction verification;
- security/privacy impact;
- test evidence;
- coverage evidence;
- provider capability evidence;
- migration/rollback information for contract changes.

A working-tree implementation is not automatically a release.

### Release reproducibility and supply-chain integrity

Every release MUST be reproducible from an identified source commit, Python interpreter version, dependency lock/constraints state, and build configuration.

Release evidence MUST include, as applicable:

- immutable source commit identifier;
- exact Python/runtime version;
- dependency lock/constraints fingerprint;
- generated SBOM;
- artifact checksum/digest;
- build/test/security-gate results;
- artifact provenance/attestation when supported by the delivery system;
- release tag/version mapping.

Release evidence MUST be materialized as **`evidence/RELEASE_PROVENANCE.json`** for every releasable artifact. The JSON artifact MUST be validated by **`G08_RELEASE_VERIFICATION`** and MUST cryptographically bind the released artifact to its source commit, dependency state, build environment, verification evidence, and artifact digest. Missing, malformed, stale, or unbound release provenance is **NOT VERIFIED** and release-blocking.

Release artifacts MUST NOT be silently rebuilt from a different dependency state. Artifact identity MUST be independently verifiable.

Architecture changes and material security/reliability trade-offs MUST have an ADR or equivalent durable decision record before release.

Operationally significant releases MUST define rollback criteria and a tested rollback path.

### Frozen-tree compatibility

The previously frozen Architecture v1.0 tree is authoritative for physical paths.

Known exchange/provider areas include:

- `ingestion/interfaces/`
- `ingestion/providers/`
- `domain_adapters/`

Strategy implementation belongs under:

- `strategy/`

These paths MUST NOT be duplicated with a parallel top-level architecture.

A separate LICENSE file, new exchange root, or new strategy root MUST NOT be introduced solely because a generic template suggests one. Legal policy may remain documented in this Kit unless the architecture is explicitly amended.

---

# 10. Per-file single-responsibility invariant

Every Python source file MUST declare exactly one primary responsibility using the `RESPONSIBILITY` field.

The declaration MUST be derived from the actual implementation and frozen-tree role. Filename-only inference, generic layer labels, or copied templates are not evidence.

A file may contain multiple cohesive functions/classes when they collectively implement the same responsibility.

Independent responsibilities MUST be separated.

Every Python source file MUST declare its current direct dependency state using `DEPENDENCIES`.

For an intentionally empty frozen skeleton:

**None declared in current skeleton implementation**

is valid only when the file truly has no runtime dependencies.

Once implementation exists, the declaration MUST reflect actual direct dependencies.

Ownership MUST separately state:

- **OWNS:** behavior/state/contracts directly controlled by the file;
- **DOES NOT OWN:** behavior/state delegated to other files/layers.

---

# 11. Per-file test and 100% coverage acceptance gate

Every testable production Python file MUST have an explicit test scope.

For each testable production file:

- statement coverage MUST be 100%;
- branch coverage MUST be 100%;
- all reachable contract-valid success paths MUST be tested;
- all reachable failure/exception paths MUST be tested;
- boundary, empty, invalid, and degraded inputs MUST be tested where the contract permits them;
- public behavior MUST be asserted, not merely executed;
- async code MUST test cancellation, timeout, and relevant concurrency/error paths;
- external I/O MUST use test doubles in unit tests;
- integration/E2E tests MUST cover real boundary behavior where mocks cannot establish it;
- `pragma: no cover` or equivalent exclusions MUST NOT be used to manufacture compliance.

An exclusion is acceptable only when the code is genuinely non-executable under the supported architecture/tooling and the exclusion is documented, reviewed, and verified separately.

100% line coverage alone is insufficient.

For critical validation, decision, risk, and architecture logic, mutation testing is a **CONDITIONAL MUST** when a supported mutation-testing tool can exercise the target. Surviving critical mutations MUST be addressed or covered by a documented exception. This requirement is authoritative under Clause 11 and MUST NOT be weakened by the generic SHOULD semantics in Clause 24.12.1.

Coverage MUST be measured with the project's authoritative CI configuration, not a developer-selected local configuration.

---

# 12. File acceptance gate

A testable implementation file is production-ready only when:

**ONE FILE → ONE PRIMARY RESPONSIBILITY → REAL DIRECT DEPENDENCIES → COMPLETE TEST CONTRACT → 100% STATEMENT + BRANCH COVERAGE → ARCHITECTURE PASS → SECURITY PASS → PASS**

Architecture tests, dependency tests, contract tests, validation tests, and integration/E2E tests are additional gates.

Non-code artifacts such as configuration, CI workflows, Dockerfiles, Makefiles, and documentation MUST use structural/behavioral validation appropriate to the artifact. Python coverage MUST NOT be falsely claimed for them.

---

# 13. Compliance audit rule

Compliance MUST be established from repository evidence.

The following are not sufficient:

- bulk header rewriting;
- copied templates;
- filename inference;
- declared architecture without implementation evidence;
- a green lint job alone;
- line coverage without branch/path verification.

If evidence is missing, the status is:

**NOT VERIFIED**

A file MUST NOT be modified merely to make its metadata appear compliant.

Audits SHOULD be repeatable and SHOULD use automated checks where practical.

---

# 14. Contract Registry

The project MUST maintain one authoritative Contract Registry for every cross-layer contract, including provider/exchange contracts.

Registry placement MUST remain inside the frozen tree.

Where the frozen architecture already provides:

- `ingestion/interfaces/` — provider/exchange contracts;
- an existing `contracts/` path — shared contracts;

those locations may be used. A new top-level directory MUST NOT be invented solely for contracts.

Each contract MUST declare:

- stable snake_case name;
- SemVer;
- owner layer;
- allowed consumers;
- forbidden consumers;
- typed signatures;
- async/sync designation for every callable;
- error taxonomy;
- idempotency semantics where applicable;
- timeout semantics where applicable;
- rate-limit semantics where applicable;
- provenance requirements where applicable;
- test scope.

Rules:

- One contract has one canonical definition.
- Shadow contracts are forbidden.
- Consumers depend on contracts, not concrete providers.
- Contract tests MUST cover valid and rejected interactions.
- Contract identity MUST be stable enough for runtime and audit tooling.

---

# 15. Temporal Integrity

Time MUST be explicit and auditable.

- Stored/transmitted timestamps MUST be UTC.
- Contract-bound timestamps MUST be timezone-aware.
- Naive datetimes MUST NOT cross architectural boundaries.
- Wall-clock UTC is used for event timestamps, storage, reconciliation, and display.
- Monotonic clocks are used for durations, timeout measurement, retry timing, and latency.
- Event ordering MUST declare its ordering basis.
- Exchange time, receipt time, processing time, and monotonic duration MUST NOT be conflated.
- Cross-exchange ordering MUST NOT assume synchronized provider clocks without verification.
- Clock-skew detection MUST be implemented or explicitly delegated to the operational boundary, with the declared threshold and response documented.
- Temporal conversions, rounding, bucketing, and normalization MUST be documented at the transformation point.

Tests MUST cover, as applicable:

- epoch zero;
- far-future values;
- timezone offsets;
- out-of-order events;
- clock skew;
- DST-related input normalization where user/provider input can contain local time;
- leap-second representations by explicitly accepting, normalizing, or rejecting them according to the contract.

Because standard Python `datetime` does not represent a leap-second value directly, the test requirement is to verify the project's declared behavior for leap-second input rather than invent an unsupported datetime representation.

---

# 16. Provenance & Traceability

Every externally sourced data unit MUST carry sufficient provenance to reconstruct origin and lifecycle.

Minimum fields:

- `source`
- `source_endpoint`
- `source_timestamp`
- `received_at`
- `ingested_at`
- `raw_hash`
- `schema_version`
- `correlation_id`
- `sequence_or_offset`, when available

Rules:

- Provenance MUST survive normalization.
- Downstream records MUST remain resolvable to their raw source record.
- No layer may fabricate provider provenance.
- Missing provenance is a data-quality event, not a silent default.
- Hashing MUST use a documented algorithm and canonical/raw-byte definition.
- Correlation IDs MUST be propagated across the lifecycle without exposing secrets.
- Duplicate identity and idempotency keys MUST be defined for data flows where replay, reconnect, retry, or persistence can duplicate records.
- The system MUST explicitly declare whether each externally driven operation is at-most-once, at-least-once, or effectively-once; "exactly once" MUST NOT be claimed without a demonstrable end-to-end guarantee.
- Canonical serialization MUST be defined wherever hashing, signatures, deduplication, or equality depends on serialized data.
- Corruption detection MUST exist for retained raw data and other integrity-critical artifacts.
- Replay/reprocessing behavior MUST be safe and testable.
- Data-quality findings such as gaps, duplicates, out-of-order data, malformed payloads, and provenance loss MUST be first-class observable events.
- Traceability MUST be tested from downstream record back to source evidence.

---

# 17. Contract Evolution Policy

Contracts are versioned artifacts.

Semantic-version rules:

- breaking change → MAJOR;
- backward-compatible feature/addition → MINOR;
- backward-compatible correction/clarification → PATCH.

Rules:

- Every contract change MUST update its SemVer.
- Breaking changes require a documented migration path.
- Deprecated fields/methods MUST identify deprecation status and removal target.
- At most two live major versions SHOULD be supported unless a documented compatibility exception is approved.
- Consumers MUST migrate in the same change set where practical, or the previous version MUST remain supported for the declared migration window.
- Runtime dispatch MUST select a declared contract version.
- Contracts MUST NOT silently change shape at runtime.
- Provider capability changes that affect the contract MUST trigger a compliance re-check before release.
- Migration tests MUST cover old/new compatibility during the migration window.
- Schema evolution MUST define additive, nullable, removal, rename, type-change, backward-compatibility, and forward-compatibility rules where schemas cross a persisted or independently deployed boundary.
- Persisted schema migrations MUST be explicit, ordered, idempotent where required, reversible where feasible, and tested against representative old data.
- Contract/schema validation MUST occur at the boundary; malformed or incompatible data MUST fail explicitly rather than being silently coerced.
- Breaking provider API changes MUST be treated as contract-impacting changes even when the local Python API remains unchanged.

---

# 18. Fault Isolation Model

Provider failures MUST NOT cascade into unrelated providers or subsystems.

Mandatory controls:

- per-provider isolation;
- bounded concurrency/bulkheads;
- explicit timeouts;
- circuit breakers with declared failure threshold, window, and cooldown;
- bounded exponential backoff with jitter;
- first-class 429/rate-limit handling;
- explicit degraded-mode behavior;
- provider-to-project error translation at the provider boundary.

Each subsystem MUST declare whether dependency failure causes:

- fail-closed;
- fail-open;
- fail-degraded;

and that behavior MUST be testable.

Provider-specific exception classes and error codes MUST NOT leak into domain, analysis, decision, or risk layers.

Tests MUST cover provider failure, timeout, rate limit, circuit opening/recovery, cancellation, and degraded operation where applicable.

### Concurrency, backpressure, and shutdown

Every asynchronous subsystem MUST declare task ownership, cancellation propagation, concurrency limits, queue bounds, overflow behavior, and shutdown semantics.

- Structured concurrency MUST be preferred.
- Task cancellation MUST propagate according to the declared ownership model.
- Queues MUST be bounded unless an explicit finite-memory proof exists.
- Queue overflow MUST have a declared policy: reject, block, shed/drop, coalesce, or persist.
- Backpressure MUST propagate toward the producer when safe.
- Lag/queue saturation thresholds MUST be observable.
- SIGTERM/SIGINT or equivalent shutdown signals MUST trigger graceful shutdown for deployable processes.
- Shutdown MUST define behavior for in-flight requests, reconnect loops, queued work, persistence, and partial operations.
- Restart/recovery behavior MUST be deterministic enough to avoid silent loss or duplication.
- Resource budgets MUST cover CPU, memory, open connections, queue depth, throughput, and event-loop lag for production-critical components, or the component MUST record N/A with a reviewed justification.

Tests MUST cover saturation, cancellation propagation, concurrent access, shutdown during I/O, restart/recovery, and overflow behavior where applicable.

---

# 19. Observability Policy

Observability MUST be structured, stable, and secret-safe.

### Logs

Use structured logs, preferably JSON, with stable fields including as applicable:

- timestamp;
- severity;
- component;
- provider;
- operation;
- correlation ID;
- contract/version;
- outcome;
- duration;
- error classification.

Logs MUST NOT contain credentials, tokens, authorization headers, or unnecessary authenticated payloads.

### Metrics

Providers and applicable layers MUST expose stable metrics for:

- request count;
- error count;
- latency;
- rate-limit events;
- circuit-breaker transitions;
- ingestion lag;
- data-quality events;
- retries.

Metric names and units MUST be documented.

### Tracing

Cross-layer traces MUST preserve correlation IDs and MUST NOT place secrets in span attributes.

### Health

Deployable components MUST distinguish liveness from readiness.

Readiness MUST reflect the dependencies necessary to perform the component's declared function; optional dependencies MUST NOT make a healthy component appear unavailable.

Observability configuration itself is subject to the same security and dependency rules.

### Operational objectives

Production-critical components MUST define applicable SLIs/SLOs or explicit operational thresholds for availability, latency, freshness/ingestion lag, error rate, and data quality. Where SLOs are not meaningful, the task MUST record N/A with justification.

Alerts MUST be actionable and tied to a documented response path. Alert thresholds MUST account for sustained failure, not only single transient events.

Operationally significant incidents MUST produce an auditable incident record and, for material incidents, a post-incident review with corrective actions.

---

# 20. Definition of Ready

A task is NOT READY until all applicable items are known:

- exactly one primary responsibility;
- frozen-tree path;
- owning layer;
- relevant contract(s) and versions;
- allowed/forbidden dependency directions;
- direct dependencies;
- test scope;
- 100% per-file coverage intent where applicable;
- integration/E2E classification;
- provider/library capability verification;
- security classification;
- privacy/data-retention impact;
- explicit non-goals;
- rollback/removal/migration path for contract changes;
- acceptance evidence required for release;
- operational runbook for failure modes introduced by the change;
- recovery/RPO/RTO impact where state or availability is affected;
- configuration and secret lifecycle impact;
- performance/resource budget impact;
- dependency/supply-chain impact;
- rollback criteria and verified rollback procedure.

### Configuration and credential lifecycle

Configuration MUST have one authoritative precedence model (for example: defaults → environment-specific configuration → environment variables/secret references, as defined by the project). Unknown or misspelled configuration keys MUST be rejected or explicitly handled; silent fallback is forbidden for security- or correctness-critical settings.

Runtime configuration MUST be validated at startup. Secrets and non-secret configuration MUST be separated. Secret values MUST never be copied into ordinary configuration artifacts, logs, crash reports, or metrics.

Credentials MUST have documented creation, scope, rotation, expiration, revocation, and compromise-response behavior where the credential system supports those controls. Revoked/expired credentials MUST fail closed.

### Resilience and recovery readiness

Stateful or availability-critical changes MUST define applicable RPO and RTO targets, backup ownership, backup integrity verification, restore procedure, and restore-test evidence. A backup that has never been restore-tested MUST NOT be treated as verified recovery capability.

Operationally significant provider failures MUST have a runbook covering outage, rate-limit storm, authentication failure, data corruption, clock skew, queue saturation, and recovery when those scenarios are applicable.

If an item is genuinely not applicable, the task MUST record **N/A with justification**, rather than leaving it ambiguous.

---

# 21. Non-Goals / Explicit Scope Exclusions

Unless the architecture is formally amended, the system does NOT include:

- HFT/co-location/microsecond-latency execution as a project objective;
- custody or wallet management;
- private-key handling for user funds;
- broker/dealer functionality;
- tax or regulatory filing on behalf of users;
- investment advice or discretionary portfolio management;
- unnecessary end-user PII;
- a simulated provider presented as a live provider;
- new top-level architecture or duplicate layer structures;
- unsupported HFT-style guarantees, microsecond determinism, or "exactly-once" claims that cannot be demonstrated;
- uncontrolled collection of telemetry or personal data merely for convenience.

Simulation/testing providers MAY exist when clearly labeled, isolated, and unable to masquerade as live providers.

A non-goal proposal requires an explicit architecture-change request.

---

# 22. Rate Limit Registry

A central Rate Limit Registry MUST be the authoritative source for provider rate-limit policy.

It MUST remain inside the frozen tree.

For each provider, record where applicable:

- REST endpoint-class limits;
- WebSocket connection/subscription limits;
- order/cancel limits when in scope;
- weighted vs. simple counting;
- burst allowance;
- status/header/retry-after semantics;
- official documentation source;
- source publication/review date;
- last verification date;
- verification status.

Limits MUST be treated as verified facts, not assumptions.

Runtime MUST honor dynamic provider signals such as `Retry-After`, remaining-weight headers, or equivalent mechanisms.

Rate limiting MUST be scoped at least by provider and endpoint class where provider semantics require it.

429/equivalent signals MUST produce bounded exponential backoff with jitter and observable events.

Tests MUST cover allowed requests, throttling, burst behavior, dynamic limits, backoff, and recovery.

A provider rate-limit change MUST trigger Registry update and compliance re-check before release.

### Provider capability matrix

The 15-provider target MUST be represented by one authoritative capability matrix. Each row MUST record verification status and date for REST, WebSocket, authentication, sandbox/testnet, market data, trading where in scope, symbol/instrument model, rate limits, and provider contract/API version.

A capability marked unknown, stale, or unsupported MUST NOT be consumed as if verified. Provider documentation evidence MUST be retained in auditable form, with the source and verification date.

---

# 23. Data Retention & Privacy

Retention MUST be explicit.

For every stored data category, define:

- purpose;
- retention period;
- owner;
- storage location;
- access policy;
- deletion/anonymization behavior;
- backup treatment.

At minimum consider:

- raw provider payloads;
- normalized market data;
- orders/fills where in scope;
- logs;
- metrics;
- error records;
- caches.

Credentials SHOULD NOT be persisted. When credentials are necessarily materialized temporarily, their lifecycle MUST be explicit and bounded.

Rules:

- raw payloads, when retained, MUST be immutable and hash-referenced;
- retention MUST be no longer than justified by purpose, integrity, debugging, or legal obligations;
- logs MUST exclude secrets, tokens, auth headers, and unnecessary user identifiers;
- PII MUST be minimized;
- required PII MUST be access-controlled and auditable;
- deletion MUST actually delete or irreversibly anonymize data;
- backups and exports inherit the applicable retention/security requirements;
- credentials MUST NOT be exported;
- retention and deletion behavior MUST be tested when owned by application code;
- infrastructure-enforced retention MUST have an auditable infrastructure control and verification procedure.
- Data MUST be classified at least by sensitivity/operational criticality sufficient to drive access, retention, logging, and export controls.
- Access to sensitive operational data MUST follow least privilege and be auditable.
- Audit records that are required for compliance MUST be protected against unauthorized alteration or deletion.

---

# 24. Global modern engineering standard

This is a **composite normative clause**. Its subsections 24.1–24.12 and Normative Appendices A–J are inseparable parts of Clause 24 and carry the same normative enforcement authority. Any reference to the **24 clauses** includes all normative content contained within Clause 24.

All Python implementation MUST follow modern, internationally recognized engineering practice **as appropriate to the frozen architecture and the declared runtime**.

This clause is a quality standard, not a requirement to use every modern language feature in every file.

### 24.1 Language and style

Code MUST follow:

- PEP 8 style guidance;
- PEP 20 principles where applicable;
- PEP 257 documentation conventions;
- PEP 484/604 typing principles;
- Python 3.13+ language and standard-library capabilities where appropriate;
- current project lint/type-check configuration.

PEP 695 type-parameter syntax, `match/case`, `typing.Self`, `ExceptionGroup`, `asyncio.TaskGroup`, and similar features SHOULD be used when they make the implementation clearer, safer, or more correct.

They MUST NOT be inserted merely to demonstrate modern syntax.

### 24.2 Design

Where compatible with the frozen architecture, use:

- Single Responsibility;
- Separation of Concerns;
- Dependency Inversion at architectural boundaries;
- explicit over implicit behavior;
- composition over inheritance unless a genuine `is-a` relationship exists;
- small, cohesive interfaces;
- deterministic behavior;
- explicit error handling;
- immutable/value-oriented data where appropriate.

### 24.3 Correctness

Avoid:

- deprecated APIs;
- dead code;
- unexplained magic values;
- hidden mutable global state;
- silent exception swallowing;
- implicit network access;
- unbounded concurrency;
- unbounded retries;
- undocumented side effects.

Constants MUST be named when their meaning is non-obvious or when changing them affects behavior.

### 24.4 Public API quality

All public APIs MUST:

- be fully typed;
- be documented;
- have explicit error behavior;
- define async/sync behavior;
- define relevant timeout/idempotency semantics;
- preserve declared contracts.

### 24.5 Determinism and reproducibility

Implementations SHOULD be deterministic for identical inputs unless nondeterminism is an explicit requirement.

Where nondeterminism is necessary, its source MUST be explicit and testable, including:

- randomness;
- current time;
- concurrency ordering;
- provider ordering;
- external state.

Tests MUST control or inject such sources where practical.

### 24.6 Modernization boundary

"Modern" MUST NOT authorize:

- a new top-level directory;
- a duplicate architecture;
- a new unregistered contract;
- bypassing a frozen layer;
- bypassing security;
- weakening tests;
- silently changing a contract.

Any modernization that changes a contract MUST follow clause 17.

### 24.7 Secure development and threat modeling

Security MUST be treated as an engineering property, not only a runtime feature.

For security-sensitive or externally exposed changes, the review MUST consider:

- trust boundaries;
- authentication and authorization;
- input validation and canonicalization;
- injection/deserialization risks;
- SSRF and unintended network destinations;
- TLS/certificate validation;
- credential exposure;
- denial-of-service/resource exhaustion;
- dependency/supply-chain risk;
- sensitive-data leakage;
- abuse/replay scenarios.

Threat-model findings that affect architecture or contracts MUST be resolved or explicitly accepted through the documented change-control process.

### 24.8 Test strategy hierarchy

Testing MUST be layered according to risk:

**Unit → Contract → Architecture/Dependency → Property/Boundary → Integration → Resilience/Failure → Security → E2E**

Where applicable, critical parsers, normalizers, validators, and state transitions SHOULD use property-based or fuzz testing. Production-critical paths MUST use load/stress/soak testing when resource behavior cannot be established by smaller tests; otherwise the task MUST document why smaller tests establish the required resource behavior.

A test layer MUST NOT be substituted by a weaker layer merely to satisfy a coverage percentage.

### 24.9 Automated enforcement and evidence model

Every mandatory rule MUST map to an auditable enforcement chain:

**RULE → OWNER → ARTIFACT → VERIFICATION METHOD → TEST/CHECK → CI GATE → EVIDENCE → RELEASE DECISION**

The repository MUST maintain an authoritative compliance matrix inside the frozen architecture or existing repository documentation structure. Each mandatory control MUST identify:

- control/rule ID;
- responsible owner;
- affected artifact/path;
- verification method;
- automated check, test, or reviewer evidence;
- CI gate;
- evidence location;
- failure status;
- release-blocking classification.

"Manual review" is not a substitute for automation when the rule is mechanically testable.

Compliance tooling MUST fail closed: missing evidence, missing control mapping, stale evidence, or an unknown verification state MUST result in **NOT VERIFIED**, not COMPLIANT.

### 24.10 CI/CD non-bypass rule

Mandatory compliance gates MUST execute for every merge/release path that can produce a production artifact.

Direct pushes, local-only checks, emergency workflows, or alternate CI workflows MUST NOT bypass mandatory architecture, security, dependency, test, provenance, or release gates.

Any emergency exception MUST be explicitly recorded with scope, reason, owner, expiry, compensating control, and follow-up remediation. Expired exceptions MUST fail the compliance audit.

### 24.11 Global acceptance rule

The implementation is compliant only when:

**Architecture + Ownership + Dependencies + Contracts + Security + Supply Chain + Temporal Integrity + Provenance + Data Integrity + Concurrency + Fault Isolation + Observability + Testing + Resilience + Privacy + Review + Reproducible Release + Modern Engineering = VERIFIED**

No single style rule may override correctness, security, architecture, or data integrity.

---

### 24.12 Normative Global Control Baseline and Executable Compliance Model

This subsection is **part of Clause 24**. It is not an additional clause. It is the mandatory operationalization of clauses 1–24 and is therefore normative.

#### 24.12.1 Requirement strength

Unless a requirement explicitly states otherwise, the following keywords are normative:

- **MUST / SHALL** — mandatory; failure is release-blocking unless an approved exception explicitly permits the deviation.
- **MUST NOT / SHALL NOT** — prohibited; violation is release-blocking unless an approved exception explicitly permits the deviation.
- **CONDITIONAL MUST** — mandatory when its stated applicability condition is true; applicability MUST itself be recorded.
- **SHOULD** — recommended default. A deviation is permitted only when documented with rationale, owner, affected control, and review evidence; a SHOULD MUST NOT silently be treated as satisfied. A control explicitly designated **CONDITIONAL MUST** elsewhere remains mandatory whenever its applicability condition is true.
- **MAY** — optional.

For critical validation, decision, risk, and architecture logic, mutation testing is a **CONDITIONAL MUST** per Clause 11 when a supported mutation-testing tool can exercise the target.

A control marked **N/A** MUST include a machine-auditable justification, an owner, and reviewer evidence. N/A without evidence is **NOT VERIFIED**.

#### 24.12.2 Canonical compliance control model

Every mandatory control MUST have one stable control ID and follow:

**RULE → OWNER → ARTIFACT → VERIFICATION METHOD → TEST/CHECK → CI GATE → EVIDENCE → RELEASE DECISION**

The canonical control record MUST contain at least:

```yaml
control_id: "<stable-id>"
rule: "<normative requirement>"
severity: "BLOCKING|NON_BLOCKING"
owner: "<role-or-owner>"
artifact: "<path-or-artifact>"
applicability: "ALWAYS|CONDITIONAL|NA"
verification: "<mechanical-check-or-review>"
ci_gate: "<named-gate>"
evidence: "<commit/build/artifact/evidence-reference>"
evidence_timestamp: "<UTC>"
evidence_input_fingerprint: "<hash-or-equivalent>"
status: "PASS|FAIL|NOT_VERIFIED|NA"
exception_id: null
```

Evidence is valid only for the exact source/artifact/configuration it verifies. Missing, stale, contradictory, or unbound evidence MUST resolve to **NOT VERIFIED**.

#### 24.12.3 Canonical registry set

The repository MUST maintain one authoritative instance of each applicable registry below. A registry MAY be embedded in an existing frozen-tree artifact when that artifact is the declared canonical location; duplicate/shadow registries are forbidden.

The canonical physical locations for the current frozen repository are:

| Registry | Canonical artifact | Canonical section/record scope |
|---|---|---|
| Contract Registry | `docs/contracts.md` | complete document |
| Provider Capability Matrix | `docs/capability-matrix.md` | provider capability records |
| Rate Limit Registry | `docs/capability-matrix.md` | rate-limit registry section/records |
| Compliance Matrix | `docs/README.md` | compliance matrix section/records |
| Exception Registry | `docs/README.md` | exception registry section/records |

These paths are repository-authoritative locators for automation. A control validator MUST resolve registry artifacts from these paths and MUST fail closed if an expected artifact/section is missing, duplicated, ambiguous, or structurally invalid. No validator may infer an alternative registry location from filename similarity or directory scanning.

The canonical structural validator is `validation/compliance_registry_validator.py`. It MUST validate the three registry artifacts and the complete G01–G08 and Appendix A–J control bindings. Its repository CI entry point is `.github/workflows/compliance-registry.yml`, mapped to `G04_ARCHITECTURE_DEPENDENCY`. A green registry-structure check does not by itself make implementation controls PASS; controls remain `NOT VERIFIED` until their authoritative evidence exists.

**Contract Registry** — one row per contract:
```yaml
contract_id: "<stable-snake-case-id>"
version: "<SemVer>"
owner_layer: "<layer>"
allowed_consumers: ["..."]
forbidden_consumers: ["..."]
signature: "<typed-signature-reference>"
async_mode: "ASYNC|SYNC"
error_taxonomy: ["..."]
idempotency: "<declared-semantics>"
timeout: "<declared-semantics>"
rate_limit: "<declared-semantics>"
provenance: "<required-fields>"
tests: ["..."]
status: "ACTIVE|DEPRECATED|RETIRED"
```

**Provider Capability Matrix** — one row per provider:
```yaml
provider: "<name>"
verified_at: "<UTC>"
evidence_source: "<official-documentation-reference>"
evidence_fingerprint: "<hash-or-equivalent>"
rest: "SUPPORTED|UNSUPPORTED|UNKNOWN"
websocket: "SUPPORTED|UNSUPPORTED|UNKNOWN"
authentication: "SUPPORTED|UNSUPPORTED|UNKNOWN"
sandbox_testnet: "SUPPORTED|UNSUPPORTED|UNKNOWN|N_A"
market_data: "SUPPORTED|UNSUPPORTED|UNKNOWN"
trading: "SUPPORTED|UNSUPPORTED|UNKNOWN|OUT_OF_SCOPE"
symbol_model: "<reference>"
rate_limit_ref: "<registry-id>"
api_contract_version: "<version-or-UNKNOWN>"
status: "VERIFIED|STALE|UNKNOWN"
```

**Rate Limit Registry** — one row per provider/endpoint class as applicable:
```yaml
rate_limit_id: "<stable-id>"
provider: "<name>"
scope: "<endpoint-class-or-connection-scope>"
limit_model: "WEIGHTED|COUNT|TOKEN_BUCKET|OTHER"
limit: "<declared-value>"
burst: "<declared-value-or-N_A>"
retry_after: "<SUPPORTED|UNSUPPORTED|UNKNOWN>"
dynamic_signals: ["..."]
official_source: "<reference>"
verified_at: "<UTC>"
evidence_fingerprint: "<hash-or-equivalent>"
status: "VERIFIED|STALE|UNKNOWN"
```

**Compliance Matrix** — one row per mandatory control:
```yaml
control_id: "<stable-id>"
artifact: "<path>"
owner: "<owner>"
verification: "<method>"
gate: "<gate-id>"
evidence: "<reference>"
status: "PASS|FAIL|NOT_VERIFIED|NA"
blocking: true
exception_id: null
```

**Exception Registry** — one row per approved deviation:
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

Exceptions MUST be narrow, time-bounded, reviewable, and attached to the exact control they affect. Expired, revoked, missing, or scope-mismatched exceptions MUST NOT satisfy a control.

#### 24.12.4 Evidence freshness and invalidation

Every evidence-producing check MUST identify the input fingerprint it verified. Source-controlled evidence is invalidated by a material change to the verified source, dependency state, configuration, registry entry, or build inputs.

Dynamic provider evidence MUST have an explicit freshness interval. If no interval is defined by the provider contract, capability and rate-limit evidence MUST be re-verified at least every 30 days and immediately after a documented provider API/rate-limit change.

Stale evidence is **NOT VERIFIED**.

#### 24.12.5 Mandatory CI gate semantics

The canonical gates are:

1. `G01_FORMAT_LINT`
2. `G02_TYPECHECK`
3. `G03_UNIT_CONTRACT`
4. `G04_ARCHITECTURE_DEPENDENCY`
5. `G05_COVERAGE`
6. `G06_SECURITY_SUPPLY_CHAIN`
7. `G07_INTEGRATION_RESILIENCE`
8. `G08_RELEASE_VERIFICATION`

Each gate MUST return a machine-readable pass/fail result. Exit code `0` means PASS; any non-zero result means FAIL. Missing output, timeout, parser failure, unknown status, or unavailable required evidence MUST be treated as FAIL/NOT VERIFIED, not PASS.

A merge/release path is valid only when all applicable blocking gates pass. A local successful run cannot override a repository CI failure. Alternate workflows MUST invoke the same authoritative gate definitions.

#### 24.12.6 Exception enforcement

An exception is valid only when its registry record is present, active, unexpired, approved by the required authority, within scope, and paired with the declared compensating control.

Exceptions MUST NOT waive security, legal, provenance, or data-integrity obligations unless the exception explicitly names the affected control and documents compensating controls and residual risk.

An expired exception is automatically failing.

#### 24.12.7 Production Python file classification for coverage

Every production Python file MUST be classified as exactly one of:

- `TESTABLE` — subject to 100% statement and branch coverage.
- `NON_TESTABLE_JUSTIFIED` — executable only in a genuinely external/tooling-controlled manner; requires explicit justification and separate structural/behavioral verification.
- `GENERATED` — generated from an identified source/generator; generator and output integrity MUST be verified and coverage requirements apply to the generator or defined executable output as appropriate.
- `PROTOCOL_ONLY` — declarations/protocols with no runtime implementation; still requires contract/type/architecture verification.

`__init__.py`, CLI entrypoints, abstract classes, migration scripts, and defensive branches are not automatically exempt. Any exemption MUST be classified and justified; `pragma: no cover` alone is never justification.

#### 24.12.8 Temporal clock authority

The project MUST define a clock authority at each deployable boundary.

- Provider/event timestamps are external facts and MUST be retained separately from local receipt/processing time.
- UTC wall clock is the source for persisted event timestamps and reconciliation.
- Monotonic clock is the source for elapsed-duration measurement, timeouts, retries, and latency.
- Clock synchronization status MUST be observable for deployable hosts where local time affects correctness.
- The applicable skew threshold and response MUST be declared.
- If the authoritative wall clock is unavailable or materially skewed, the system MUST enter its declared degraded/fail-closed behavior rather than silently fabricating timestamps.

#### 24.12.9 Persistence and crash-consistency boundary

Every state-changing ingestion or external mutation MUST declare:

- transaction/commit boundary;
- atomicity expectation;
- duplicate identity;
- retry/replay behavior;
- partial-write behavior;
- crash/restart recovery behavior;
- ordering guarantee;
- durability expectation.

A successful acknowledgement MUST NOT be emitted before the declared durability/commit boundary is satisfied. If the architecture cannot guarantee exactly-once behavior, it MUST explicitly declare at-most-once, at-least-once, or effectively-once semantics.

#### 24.12.10 Security severity and remediation gate

Security findings MUST be classified using an authoritative scanner/severity scheme or documented equivalent.

- Confirmed leaked secrets: BLOCKING.
- Critical exploitable vulnerabilities: BLOCKING unless an active, approved, time-bounded exception exists.
- High-severity exploitable vulnerabilities: BLOCKING unless an active, approved, time-bounded exception exists.
- Medium/low findings: MUST have an owner and remediation target before release; release handling MUST be recorded by policy.
- Secret-scan parser failures or unavailable mandatory security evidence: NOT VERIFIED and release-blocking.

Security exceptions MUST NOT silently convert a failed control into PASS.

#### 24.12.11 Release-environment fingerprint

Release evidence MUST identify, where relevant:

- source commit;
- OS/platform and architecture;
- exact Python interpreter/build;
- dependency lock/constraints fingerprint;
- build toolchain/configuration;
- relevant environment/configuration inputs;
- locale/timezone assumptions;
- generated SBOM;
- artifact digest;
- test/security results;
- provenance/attestation where supported.

The artifact tested MUST be byte-identical to, or cryptographically bound to, the artifact released. Silent rebuilds are prohibited.

#### 24.12.12 Supply-chain and operational controls

The following controls are mandatory consequences of this clause and MUST be represented in the Compliance Matrix:

- dependency pinning, integrity verification, vulnerability/SCA scanning, provenance, transitive dependency audit, license review, dependency-confusion/typosquat review, and artifact-matched SBOM;
- secret/credential lifecycle: issue → scope → store → use → rotate → expire/revoke → compromise response → audit;
- idempotency/replay semantics for retries, reconnects, pagination overlap, redelivery, restart, and manual reprocessing;
- explicit resource budgets or justified N/A for CPU, memory, queues, connections, concurrency, throughput, retry volume, and event-loop lag;
- RPO/RTO, backup ownership/frequency, integrity verification, restore procedure, and restore-test evidence for stateful/availability-critical components;
- runbooks for provider outage, rate-limit storm, credential failure/compromise, data corruption, clock skew, queue saturation, contract incompatibility, and failed deployment where applicable;
- ADR/equivalent durable decisions for material architecture changes, cross-layer dependencies, breaking contracts, persistence semantics, security exceptions, and resilience trade-offs;
- incident records with owner/verification for corrective actions and control review for repeated material incidents.

#### 24.12.13 Final fail-closed rule

The repository MUST NOT label a change **COMPLIANT** if any applicable mandatory control is failing, missing, stale, contradictory, unverifiable, bypassed, or covered only by an invalid/unapproved exception.

The only valid compliance states remain:

**COMPLIANT / NOT COMPLIANT / NOT VERIFIED / NOT READY**



## Compliance status model

Every audited file/change MUST resolve to one of:

- **COMPLIANT** — all applicable mandatory requirements are verified.
- **NOT COMPLIANT** — one or more mandatory requirements fail.
- **NOT VERIFIED** — evidence is insufficient.
- **NOT READY** — Definition of Ready is incomplete.

"Not verified" MUST NOT be represented as "compliant".

## Change-control rule

Any change to this Compliance Kit itself is a policy/architecture change and MUST be reviewed as such. Silent weakening of a requirement is forbidden.

Clause 24 is a composite clause: its subsections 24.1–24.12 and Normative Appendices A–J are inseparable and carry the same normative authority. Any reference to the “24 clauses” includes all normative content contained within Clause 24.

The README is the source of truth for these 24 clauses. If implementation, tests, tooling, or documentation disagree with it, the disagreement MUST be resolved explicitly rather than silently ignored.


---

### 24.12 Normative Global Control Baseline and Executable Compliance Model

This subsection is **part of Clause 24**. It is not an additional clause. It is the mandatory operationalization of clauses 1–24 and is therefore normative.

#### 24.12.1 Requirement strength

Unless a requirement explicitly states otherwise, the following keywords are normative:

- **MUST / SHALL** — mandatory; failure is release-blocking unless an approved exception explicitly permits the deviation.
- **MUST NOT / SHALL NOT** — prohibited; violation is release-blocking unless an approved exception explicitly permits the deviation.
- **CONDITIONAL MUST** — mandatory when its stated applicability condition is true; applicability MUST itself be recorded.
- **SHOULD** — recommended default. A deviation is permitted only when documented with rationale, owner, affected control, and review evidence; a SHOULD MUST NOT silently be treated as satisfied. A control explicitly designated **CONDITIONAL MUST** elsewhere remains mandatory whenever its applicability condition is true.
- **MAY** — optional.

For critical validation, decision, risk, and architecture logic, mutation testing is a **CONDITIONAL MUST** per Clause 11 when a supported mutation-testing tool can exercise the target.

A control marked **N/A** MUST include a machine-auditable justification, an owner, and reviewer evidence. N/A without evidence is **NOT VERIFIED**.

#### 24.12.2 Canonical compliance control model

Every mandatory control MUST have one stable control ID and follow:

**RULE → OWNER → ARTIFACT → VERIFICATION METHOD → TEST/CHECK → CI GATE → EVIDENCE → RELEASE DECISION**

The canonical control record MUST contain at least:

```yaml
control_id: "<stable-id>"
rule: "<normative requirement>"
severity: "BLOCKING|NON_BLOCKING"
owner: "<role-or-owner>"
artifact: "<path-or-artifact>"
applicability: "ALWAYS|CONDITIONAL|NA"
verification: "<mechanical-check-or-review>"
ci_gate: "<named-gate>"
evidence: "<commit/build/artifact/evidence-reference>"
evidence_timestamp: "<UTC>"
evidence_input_fingerprint: "<hash-or-equivalent>"
status: "PASS|FAIL|NOT_VERIFIED|NA"
exception_id: null
```

Evidence is valid only for the exact source/artifact/configuration it verifies. Missing, stale, contradictory, or unbound evidence MUST resolve to **NOT VERIFIED**.

#### 24.12.3 Canonical registry set

The repository MUST maintain one authoritative instance of each applicable registry below. A registry MAY be embedded in an existing frozen-tree artifact when that artifact is the declared canonical location; duplicate/shadow registries are forbidden.

The canonical physical locations for the current frozen repository are:

| Registry | Canonical artifact | Canonical section/record scope |
|---|---|---|
| Contract Registry | `docs/contracts.md` | complete document |
| Provider Capability Matrix | `docs/capability-matrix.md` | provider capability records |
| Rate Limit Registry | `docs/capability-matrix.md` | rate-limit registry section/records |
| Compliance Matrix | `docs/README.md` | compliance matrix section/records |
| Exception Registry | `docs/README.md` | exception registry section/records |

These paths are repository-authoritative locators for automation. A control validator MUST resolve registry artifacts from these paths and MUST fail closed if an expected artifact/section is missing, duplicated, ambiguous, or structurally invalid. No validator may infer an alternative registry location from filename similarity or directory scanning.

**Contract Registry** — one row per contract:
```yaml
contract_id: "<stable-snake-case-id>"
version: "<SemVer>"
owner_layer: "<layer>"
allowed_consumers: ["..."]
forbidden_consumers: ["..."]
signature: "<typed-signature-reference>"
async_mode: "ASYNC|SYNC"
error_taxonomy: ["..."]
idempotency: "<declared-semantics>"
timeout: "<declared-semantics>"
rate_limit: "<declared-semantics>"
provenance: "<required-fields>"
tests: ["..."]
status: "ACTIVE|DEPRECATED|RETIRED"
```

**Provider Capability Matrix** — one row per provider:
```yaml
provider: "<name>"
verified_at: "<UTC>"
evidence_source: "<official-documentation-reference>"
evidence_fingerprint: "<hash-or-equivalent>"
rest: "SUPPORTED|UNSUPPORTED|UNKNOWN"
websocket: "SUPPORTED|UNSUPPORTED|UNKNOWN"
authentication: "SUPPORTED|UNSUPPORTED|UNKNOWN"
sandbox_testnet: "SUPPORTED|UNSUPPORTED|UNKNOWN|N_A"
market_data: "SUPPORTED|UNSUPPORTED|UNKNOWN"
trading: "SUPPORTED|UNSUPPORTED|UNKNOWN|OUT_OF_SCOPE"
symbol_model: "<reference>"
rate_limit_ref: "<registry-id>"
api_contract_version: "<version-or-UNKNOWN>"
status: "VERIFIED|STALE|UNKNOWN"
```

**Rate Limit Registry** — one row per provider/endpoint class as applicable:
```yaml
rate_limit_id: "<stable-id>"
provider: "<name>"
scope: "<endpoint-class-or-connection-scope>"
limit_model: "WEIGHTED|COUNT|TOKEN_BUCKET|OTHER"
limit: "<declared-value>"
burst: "<declared-value-or-N_A>"
retry_after: "<SUPPORTED|UNSUPPORTED|UNKNOWN>"
dynamic_signals: ["..."]
official_source: "<reference>"
verified_at: "<UTC>"
evidence_fingerprint: "<hash-or-equivalent>"
status: "VERIFIED|STALE|UNKNOWN"
```

**Compliance Matrix** — one row per mandatory control:
```yaml
control_id: "<stable-id>"
artifact: "<path>"
owner: "<owner>"
verification: "<method>"
gate: "<gate-id>"
evidence: "<reference>"
status: "PASS|FAIL|NOT_VERIFIED|NA"
blocking: true
exception_id: null
```

**Exception Registry** — one row per approved deviation:
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

Exceptions MUST be narrow, time-bounded, reviewable, and attached to the exact control they affect. Expired, revoked, missing, or scope-mismatched exceptions MUST NOT satisfy a control.

#### 24.12.4 Evidence freshness and invalidation

Every evidence-producing check MUST identify the input fingerprint it verified. Source-controlled evidence is invalidated by a material change to the verified source, dependency state, configuration, registry entry, or build inputs.

Dynamic provider evidence MUST have an explicit freshness interval. If no interval is defined by the provider contract, capability and rate-limit evidence MUST be re-verified at least every 30 days and immediately after a documented provider API/rate-limit change.

Stale evidence is **NOT VERIFIED**.

#### 24.12.5 Mandatory CI gate semantics

The canonical gates are:

1. `G01_FORMAT_LINT`
2. `G02_TYPECHECK`
3. `G03_UNIT_CONTRACT`
4. `G04_ARCHITECTURE_DEPENDENCY`
5. `G05_COVERAGE`
6. `G06_SECURITY_SUPPLY_CHAIN`
7. `G07_INTEGRATION_RESILIENCE`
8. `G08_RELEASE_VERIFICATION`

Each gate MUST return a machine-readable pass/fail result. Exit code `0` means PASS; any non-zero result means FAIL. Missing output, timeout, parser failure, unknown status, or unavailable required evidence MUST be treated as FAIL/NOT VERIFIED, not PASS.

A merge/release path is valid only when all applicable blocking gates pass. A local successful run cannot override a repository CI failure. Alternate workflows MUST invoke the same authoritative gate definitions.

#### 24.12.6 Exception enforcement

An exception is valid only when its registry record is present, active, unexpired, approved by the required authority, within scope, and paired with the declared compensating control.

Exceptions MUST NOT waive security, legal, provenance, or data-integrity obligations unless the exception explicitly names the affected control and documents compensating controls and residual risk.

An expired exception is automatically failing.

#### 24.12.7 Production Python file classification for coverage

Every production Python file MUST be classified as exactly one of:

- `TESTABLE` — subject to 100% statement and branch coverage.
- `NON_TESTABLE_JUSTIFIED` — executable only in a genuinely external/tooling-controlled manner; requires explicit justification and separate structural/behavioral verification.
- `GENERATED` — generated from an identified source/generator; generator and output integrity MUST be verified and coverage requirements apply to the generator or defined executable output as appropriate.
- `PROTOCOL_ONLY` — declarations/protocols with no runtime implementation; still requires contract/type/architecture verification.

`__init__.py`, CLI entrypoints, abstract classes, migration scripts, and defensive branches are not automatically exempt. Any exemption MUST be classified and justified; `pragma: no cover` alone is never justification.

#### 24.12.8 Temporal clock authority

The project MUST define a clock authority at each deployable boundary.

- Provider/event timestamps are external facts and MUST be retained separately from local receipt/processing time.
- UTC wall clock is the source for persisted event timestamps and reconciliation.
- Monotonic clock is the source for elapsed-duration measurement, timeouts, retries, and latency.
- Clock synchronization status MUST be observable for deployable hosts where local time affects correctness.
- The applicable skew threshold and response MUST be declared.
- If the authoritative wall clock is unavailable or materially skewed, the system MUST enter its declared degraded/fail-closed behavior rather than silently fabricating timestamps.

#### 24.12.9 Persistence and crash-consistency boundary

Every state-changing ingestion or external mutation MUST declare:

- transaction/commit boundary;
- atomicity expectation;
- duplicate identity;
- retry/replay behavior;
- partial-write behavior;
- crash/restart recovery behavior;
- ordering guarantee;
- durability expectation.

A successful acknowledgement MUST NOT be emitted before the declared durability/commit boundary is satisfied. If the architecture cannot guarantee exactly-once behavior, it MUST explicitly declare at-most-once, at-least-once, or effectively-once semantics.

#### 24.12.10 Security severity and remediation gate

Security findings MUST be classified using an authoritative scanner/severity scheme or documented equivalent.

- Confirmed leaked secrets: BLOCKING.
- Critical exploitable vulnerabilities: BLOCKING unless an active, approved, time-bounded exception exists.
- High-severity exploitable vulnerabilities: BLOCKING unless an active, approved, time-bounded exception exists.
- Medium/low findings: MUST have an owner and remediation target before release; release handling MUST be recorded by policy.
- Secret-scan parser failures or unavailable mandatory security evidence: NOT VERIFIED and release-blocking.

Security exceptions MUST NOT silently convert a failed control into PASS.

#### 24.12.11 Release-environment fingerprint

Release evidence MUST identify, where relevant:

- source commit;
- OS/platform and architecture;
- exact Python interpreter/build;
- dependency lock/constraints fingerprint;
- build toolchain/configuration;
- relevant environment/configuration inputs;
- locale/timezone assumptions;
- generated SBOM;
- artifact digest;
- test/security results;
- provenance/attestation where supported.

The artifact tested MUST be byte-identical to, or cryptographically bound to, the artifact released. Silent rebuilds are prohibited.

#### 24.12.12 Supply-chain and operational controls

The following controls are mandatory consequences of this clause and MUST be represented in the Compliance Matrix:

- dependency pinning, integrity verification, vulnerability/SCA scanning, provenance, transitive dependency audit, license review, dependency-confusion/typosquat review, and artifact-matched SBOM;
- secret/credential lifecycle: issue → scope → store → use → rotate → expire/revoke → compromise response → audit;
- idempotency/replay semantics for retries, reconnects, pagination overlap, redelivery, restart, and manual reprocessing;
- explicit resource budgets or justified N/A for CPU, memory, queues, connections, concurrency, throughput, retry volume, and event-loop lag;
- RPO/RTO, backup ownership/frequency, integrity verification, restore procedure, and restore-test evidence for stateful/availability-critical components;
- runbooks for provider outage, rate-limit storm, credential failure/compromise, data corruption, clock skew, queue saturation, contract incompatibility, and failed deployment where applicable;
- ADR/equivalent durable decisions for material architecture changes, cross-layer dependencies, breaking contracts, persistence semantics, security exceptions, and resilience trade-offs;
- incident records with owner/verification for corrective actions and control review for repeated material incidents.

#### 24.12.13 Final fail-closed rule

The repository MUST NOT label a change **COMPLIANT** if any applicable mandatory control is failing, missing, stale, contradictory, unverifiable, bypassed, or covered only by an invalid/unapproved exception.

The only valid compliance states remain:

**COMPLIANT / NOT COMPLIANT / NOT VERIFIED / NOT READY**



## Normative Appendices A–J

Appendices A–J are **normative parts of Clause 24.12** and carry the same enforcement weight as all other mandatory requirements of this Compliance Kit. They are not informational guidance and MUST be included in compliance evaluation, CI enforcement, evidence generation, and release decisions.

### Appendix locator rule

The ten appendices below are part of the canonical control baseline. Their control IDs, evidence, validators, and CI gates MUST be represented in the Compliance Matrix; omission of an appendix from tooling is a compliance failure.

## A. Dependency and supply-chain security

1. Production dependencies MUST be pinned through the authoritative lock/constraints mechanism.
2. Integrity hashes MUST be used where supported by the package/build ecosystem.
3. Dependency vulnerability scanning MUST run in CI.
4. Dependency provenance and transitive dependencies MUST be auditable.
5. Dependency license obligations MUST be checked before release.
6. Typosquatting/dependency-confusion risk MUST be considered for new dependencies.
7. The generated SBOM MUST correspond to the actual release artifact.
8. A dependency with a critical exploitable vulnerability MUST block release unless an explicit, time-bounded exception with compensating controls is approved.

## B. Build and artifact integrity

The canonical release provenance evidence artifact is **`evidence/RELEASE_PROVENANCE.json`**, using the repository's existing `evidence/` path. It is generated/materialized for each releasable artifact and MUST NOT be treated as a source-controlled static claim when its contents are release-specific.

1. A release MUST identify the exact source commit, interpreter, dependency state, build configuration, and artifact digest.
2. Release artifacts MUST be immutable after publication.
3. Rebuilding the same release inputs MUST produce the same artifact or a documented deterministic-equivalence proof.
4. Artifact provenance/attestation MUST be generated when supported by the build infrastructure. If the infrastructure does not support it, the release evidence MUST record that limitation as N/A with justification.
5. The release process MUST verify that the artifact tested is the artifact released.

## C. Secret and credential lifecycle

Credential handling MUST define, where supported:
**issue → scope → store → use → rotate → expire/revoke → compromise response → audit**.

A credential compromise MUST have a documented containment path, including revocation/rotation and evidence review.

## D. Idempotency and replay

Every ingestion or externally triggered mutation MUST define its duplicate identity and replay semantics. Retries, reconnects, pagination overlap, provider redelivery, process restart, and manual reprocessing MUST be considered.

## E. Performance and resource safety

Production-critical components MUST have explicit or justified-N/A budgets for:
CPU, memory, queue depth, open connections, request concurrency, throughput, retry volume, and event-loop lag.

Resource exhaustion MUST be observable and MUST degrade according to a declared policy rather than fail unpredictably.

## F. Disaster recovery and continuity

For stateful/availability-critical components, the repository or operational control plane MUST document:
RPO, RTO, backup owner, backup frequency, integrity verification, restore procedure, restore-test frequency, and recovery evidence.

## G. Runbooks

For each production-critical failure mode, the operational owner MUST have a runbook covering detection, containment, diagnosis, recovery, verification, and rollback/escalation as applicable.

At minimum, applicable runbooks MUST address:
provider outage, rate-limit storm, credential failure/compromise, data corruption, clock skew, queue saturation, contract incompatibility, and failed deployment.

## H. Architecture decisions

Material architecture changes, new cross-layer dependencies, contract-breaking changes, persistence semantics, security exceptions, and resilience trade-offs MUST have a durable ADR/equivalent decision record.

## I. Incident and post-incident control

Material production incidents MUST be recorded. Corrective actions MUST have an owner and verification method. Repeated incidents MUST trigger a review of the underlying control rather than only a local workaround.

## J. Final fail-closed rule

The repository MUST NOT label a change **COMPLIANT** if any mandatory control is:
- failing;
- missing;
- stale;
- contradictory;
- unverifiable;
- bypassed;
- or covered only by an unapproved exception.

The only valid states remain:

**COMPLIANT / NOT COMPLIANT / NOT VERIFIED / NOT READY**
