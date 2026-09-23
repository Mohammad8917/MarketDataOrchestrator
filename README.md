
MarketDataOrchestrator
Architecture Frozen v1.0.

Layered, event-driven market-data and analysis orchestrator for Crypto, Forex, and Gold.

The repository structure is intentionally frozen. Implementation must preserve the documented layer boundaries, contracts, temporal integrity, traceability, and validation ownership.

🔴 MANDATORY KIT ENTRY GATE
Every time the MarketDataOrchestrator Compliance Kit is opened, the first action MUST be to check this Compliance Kit before doing anything else.

This is a mandatory precondition for all work on this repository.

Required order:

text
ENTER KIT → CHECK COMPLIANCE KIT → VERIFY REQUEST AGAINST KIT → ONLY THEN PROCEED
Before any analysis, design, code generation, file modification, commit, or repository change:

Re-check the current Architecture & Implementation Compliance Kit.

Verify the requested work against its rules, frozen repository tree, layer boundaries, dependency rules, contracts, invariants, and Definition of Done.

Only after that check may implementation or repository changes proceed.

This check must be performed again on every new entry into the Kit, even if it was checked earlier in the same conversation, task, or project.

No implementation work may bypass this gate.

🔴 CODING STANDARDS & COMPLIANCE — MANDATORY
Owner / Author: محمد حسن زاده
License policy: Proprietary — All Rights Reserved
Target runtime: Python 3.13+
Exchange integration target: 15 exchanges, subject to provider/API capability verification.

1. Mandatory source-file header
Before writing or modifying executable Python code in this repository, the file MUST begin with a project-compliance header containing, at minimum:

file name

Kit/repository address

file SemVer

Persian and Gregorian date

author: محمد حسن زاده

responsibility of the file

direct dependencies and versions

Python compatibility: 3.13+

proprietary/all-rights-reserved notice

unauthorized-use warning

project compliance reference

The header must also identify the file's architectural responsibility and its direct dependencies so that ownership and dependency direction are visible from the file itself.

For Python files, the header must remain valid Python syntax (normally a module docstring). Non-Python files must use the native comment/documentation syntax appropriate to that file type.

2. Unauthorized-use notice
Project source files may contain a notice that unauthorized copying, redistribution, modification, reverse engineering, sale, or other use without written authorization is prohibited.

Any reference to legal enforcement must be treated as a project legal notice, not a substitute for legal advice, and must not assert that a particular remedy is guaranteed. Applicable rights and remedies depend on the governing law and the facts of the case.

Owner: محمد حسن زاده.

3. Version and date
Every newly written or materially modified source file must carry its own SemVer file version and date in its header.

Repository-level release versioning remains governed by the project's SemVer policy, VERSION, CHANGELOG, and Git tags.

4. Python compatibility
New Python implementation MUST target Python 3.13+ and use modern typing and asyncio facilities where appropriate.

Compatibility claims must be verified by CI rather than assumed. Code must not rely on APIs removed or deprecated for the declared target without an explicit compatibility decision.

5. Architecture ownership and dependencies
Every implementation file must state:

its single primary responsibility;

its direct dependencies;

the architectural layer/subsystem it belongs to;

any important dependency-direction constraint.

No file may silently cross the frozen layer boundaries.

6. Async-first and security requirements
For exchange/network integrations:

async-first design is mandatory;

blocking I/O is forbidden on the event loop;

secrets must come only from environment/secret-management infrastructure;

secrets must never be committed or logged;

rate limiting is mandatory;

HTTP 429 handling requires exponential backoff;

exchange failures require contextual, secret-safe errors;

exchange connectors require isolation behind shared interfaces.

7. Exchange integration target
The system target is integration capability for at least these 15 exchanges:

Binance

Coinbase

Kraken

KuCoin

OKX

Bybit

Gate.io

HTX (Huobi)

Bitfinex

Bitstamp

MEXC

Crypto.com

Bitget

Gemini

Upbit

Each integration must conform to the project's shared provider contract and must not leak exchange-specific implementation details into domain, analysis, decision, risk, or other prohibited layers.

Actual REST/WebSocket/Testnet availability must be verified against current official exchange/provider documentation before implementation or release; capabilities must not be represented as available when the upstream service does not support them.

8. Testing and quality gates
New implementation is expected to satisfy:

complete type hints;

docstrings for public classes/functions/methods;

Ruff/flake8-compatible linting policy;

mypy-compatible type checking;

pytest + pytest-asyncio tests where async behavior exists;

mocked exchange calls in tests;

per-file statement and branch coverage: 100% acceptance gate defined below;

aggregate coverage may be reported separately but MUST NOT override a failed per-file 100% gate;

architecture and dependency tests;

CI verification before merge.

9. Review workflow
Implementation follows:

text
DRAFT → SELF-REVIEW → PEER-REVIEW → APPROVED → RELEASED
No implementation should be treated as released merely because it exists in the working tree.

⚠️ Frozen-tree compatibility note
The repository's previously frozen Architecture v1.0 tree is authoritative for physical paths. The user-provided generic project_root/exchanges/, strategies/, LICENSE, and requirements.txt layout is therefore not adopted as a new directory structure.

The existing architecture maps exchange integrations under:

ingestion/interfaces/

ingestion/providers/

domain_adapters/

and strategy implementation under:

strategy/

This preserves the repository's existing layer contracts and avoids introducing duplicate architecture.

Likewise, the legal/ownership requirements above are recorded as project policy; a separate LICENSE file is not added because it is outside the currently frozen tree unless the tree is explicitly unfrozen.

🔐 Security baseline
API keys, secrets, passwords, tokens, and private credentials MUST NOT appear in source code, logs, commits, test fixtures, or error messages.

Sensitive configuration must be externalized. Logging must mask sensitive values. Exchange credentials must never be sent to third parties except the intended provider/API endpoint and only as required by the provider contract.

📌 Compliance rule for future coding
Before every coding change:

text
ENTER KIT → CHECK COMPLIANCE KIT → VERIFY REQUEST AGAINST KIT → ONLY THEN PROCEED
If the requested change conflicts with the frozen architecture, ownership boundaries, security policy, provider contracts, or another mandatory rule, implementation must stop and the conflict must be reported before code is produced.

10. Per-file single-responsibility invariant
Every Python source file MUST declare exactly one primary responsibility in its header using the RESPONSIBILITY field. The declaration MUST be derived from the file's actual architectural role and verified against its implementation or frozen placeholder contract. A generic template, filename-only inference, or layer-wide label is NOT evidence of compliance.

A file may contain multiple functions, methods, or classes only when they are cohesive implementation elements of that one primary responsibility. Independent responsibilities MUST NOT be co-located merely because they belong to the same layer or subsystem.

Every Python source file MUST declare its current direct dependency state in DEPENDENCIES. In the frozen skeleton, where no runtime dependency is actually present, the correct value is "None declared in current skeleton implementation". Once implementation exists, DEPENDENCIES MUST list the actual direct dependencies (including relevant versions where applicable). Generic architectural permissions MUST NOT be presented as runtime dependencies.

For every audited file, ownership boundaries MUST distinguish what the file OWNS from what it DOES NOT OWN. Allowed architectural dependencies and forbidden dependencies are separate audit properties and MUST NOT be confused with current direct dependencies.

11. Per-file test and 100% coverage acceptance gate
Every testable implementation file MUST have an explicit test scope and MUST be independently verifiable against its declared responsibility.

For every testable production Python file:

Statement coverage MUST be 100%.

Branch coverage MUST be 100%.

All reachable success paths MUST be tested.

All reachable failure and exception paths MUST be tested.

Boundary, empty, invalid, and degraded-input behavior MUST be tested wherever the contract permits those states.

Public behavior and contract boundaries MUST be verified, not merely executed.

Async behavior MUST include cancellation, timeout, and relevant concurrency/error paths where applicable.

External I/O MUST be isolated behind test doubles in unit tests unless explicitly classified as integration/E2E.

pragma: no cover and equivalent exclusions MUST NOT be used to manufacture compliance. Any unavoidable exclusion requires explicit architectural justification and separate review.

100% line coverage alone is NOT sufficient for acceptance.

Mutation testing SHOULD be used for critical decision, risk, validation, and architecture logic; surviving mutations in critical logic are grounds for rejection until the weakness is resolved.

Missing tests, incomplete required paths, or coverage below 100% means NOT COMPLIANT.

The historical project-wide 80% coverage target is superseded for per-file acceptance by this 100% gate. It MUST NOT be used to approve an individual file that fails the 100% requirement.

12. File acceptance gate
A testable implementation file is accepted only when all mandatory gates pass:

text
ONE FILE → ONE PRIMARY RESPONSIBILITY → EXPLICIT REAL DEPENDENCIES
→ COMPLETE TEST CONTRACT → 100% REQUIRED COVERAGE → PASS
If any mandatory gate fails, the file is REJECTED and MUST NOT be treated as production-ready or released.

Architecture tests, dependency-direction tests, contract tests, validation tests, and integration/E2E tests remain additional requirements; they do not replace the per-file 100% requirement.

Non-code artifacts such as configuration, CI workflows, Dockerfiles, Makefiles, and scripts MUST use an appropriate structural/behavioral validation gate rather than falsely claiming Python line coverage.

13. Compliance audit rule
No bulk header rewrite may be used as proof of architectural compliance. Responsibility, dependencies, ownership, allowed/forbidden dependency direction, and test compliance MUST be established from the actual repository state. If evidence is insufficient, the result is NOT VERIFIED and the file MUST NOT be modified merely to make its header appear compliant.

text
═══════════════════════════════════════════════════════════════════════
APPENDIX A — ADDITIVE EXTENSIONS TO THE COMPLIANCE KIT
Status       : ADDITIVE ONLY — no existing clause removed or modified
Owner        : محمد حسن زاده
License      : Proprietary — All Rights Reserved
Runtime      : Python 3.13+
Authority    : This appendix is subordinate to the existing Kit. In case of
               conflict, the original Kit clauses (1–13) prevail. Nothing in
               this appendix overrides, weakens, or replaces clauses 1–13.
═══════════════════════════════════════════════════════════════════════
14. Contract Registry (Provider & Internal Contracts)
The project MUST maintain a single authoritative Contract Registry that defines every cross-layer contract used in the system, including but not limited to provider/exchange contracts.

Registry location (frozen-tree compatible):

ingestion/interfaces/ → provider/exchange contracts

contracts/ (only if already present in the frozen tree; otherwise use the closest existing layer path already defined by the frozen tree — no new top-level directory may be invented)

Each contract MUST declare:

contract name (stable identifier, snake_case)

contract version (SemVer)

owner layer

allowed consumers (layers)

forbidden consumers (layers)

method/property signatures with full type hints

async/sync designation for every callable

documented error taxonomy

idempotency semantics (where applicable)

rate-limit expectations (where applicable)

test scope reference

Rules:

A contract MUST NOT be duplicated. One contract → one canonical file.

No layer may define a "shadow contract" that re-declares an existing contract with a different shape.

Consumer code MUST depend on the contract, never on a concrete provider implementation.

Contract files MUST themselves satisfy the per-file header and single-responsibility rules (clauses 1 and 10).

Contract tests are mandatory and MUST cover both success and rejection paths of the contract boundary.

15. Temporal Integrity
All time handling across the system MUST be explicit, uniform, and auditable.

Mandatory rules:

Timestamps stored or transmitted MUST be UTC.

Every timestamp MUST be timezone-aware. Naive datetimes are forbidden at contract boundaries.

Wall-clock time and monotonic time MUST be distinguished:

Wall-clock (UTC) for storage, display, reconciliation.

Monotonic clock for latency, timeouts, and interval measurement.

Clock skew between host, exchange, and internal services MUST be detected and reported (NTP/chrony health is an operational concern; skew beyond a declared threshold MUST raise a warning or error).

All event ordering that depends on time MUST declare its ordering basis (exchange timestamp vs. local receipt time vs. monotonic).

Cross-exchange time comparison MUST NOT assume synchronized clocks unless explicitly verified per provider.

Any temporal transformation (conversion, rounding, bucketing) MUST be documented at the point of transformation.

Tests MUST include boundary cases: leap seconds (if applicable), DST-irrelevant because UTC-only, epoch zero, far-future timestamps, and out-of-order arrival.

16. Provenance & Traceability Schema
Every externally sourced data unit (tick, trade, order book snapshot, candle, order update, fill, cancellation, error event) MUST carry provenance metadata sufficient to reconstruct its origin and lifecycle.

Minimum provenance fields:

source — provider/exchange identifier

source_endpoint — endpoint or channel used

source_timestamp — provider-reported time (UTC, tz-aware)

received_at — local receipt time (UTC, tz-aware)

ingested_at — pipeline entry time (UTC, tz-aware)

raw_hash — hash of the raw payload as received

schema_version — provenance schema version (SemVer)

correlation_id — trace correlation across layers

sequence_or_offset — provider sequence number or offset when available

Rules:

Provenance MUST survive normalization. Domain objects MUST NOT lose the ability to be traced back to the raw source record.

No layer may fabricate provenance fields. Missing provenance is a data-quality event, not a silent default.

Data-quality findings (gaps, duplicates, out-of-order, corrupt payloads) MUST be recorded as first-class events, not swallowed.

Traceability MUST be testable: tests MUST verify that a given downstream record can be resolved back to its raw source record.

17. Contract Evolution Policy
Contracts in the Registry (clause 14) are versioned artifacts and MUST evolve under an explicit policy.

Rules:

Every contract change MUST bump the contract's SemVer.

Backward-incompatible changes MUST bump MAJOR and MUST NOT be shipped without a documented migration path.

Backward-compatible additive changes MUST bump MINOR.

Clarifications and bug fixes with no signature change MUST bump PATCH.

A contract MAY have at most two live MAJOR versions at any time; deprecation windows MUST be declared in the contract file.

Deprecated fields/methods MUST be marked in the contract and in code, with a stated removal date or version.

Consumers MUST be updated in the same change set as the contract bump, OR the old version MUST remain served until consumers migrate.

Provider-side capability changes (REST/WS/Testnet availability, symbol lists, rate limits) MUST be tracked as contract-relevant events and MUST trigger a compliance re-check before the next release.

No contract may be silently changed at runtime. Runtime dispatch must select a declared contract version.

18. Fault Isolation Model
Exchange/provider failures MUST NOT cascade into unrelated subsystems.

Mandatory isolation properties:

Per-exchange isolation: one provider outage MUST NOT stop ingestion, analysis, or decision layers from operating on other providers.

Circuit breaker: each provider call path MUST have an explicit circuit breaker with declared thresholds (failure count, window, cooldown).

Bulkhead: concurrent calls to a provider MUST be bounded by a declared concurrency limit per provider and per call type.

Timeouts: every external call MUST have an explicit timeout. No unbounded waits are permitted on the event loop.

Retry policy: retries MUST use exponential backoff with jitter and a hard cap. HTTP 429 MUST be treated as a first-class rate-limit signal.

Degraded mode: each layer MUST declare its behavior when an upstream dependency is unavailable (fail-open, fail-closed, or fail-degraded), and this declaration MUST be testable.

Error surface: provider-specific exceptions MUST be translated at the provider boundary into project-defined error types (clause 7 of the Kit). Exchange-specific error codes MUST NOT leak into domain, analysis, decision, or risk layers.

Isolation behavior MUST be covered by tests, including simulated provider failure, timeout, and rate-limit responses.

19. Observability Policy
Logging (as required by the Kit) is necessary but not sufficient.

Required observability surfaces:

Structured logs (JSON), with stable field names, correlation IDs, and mandatory secret masking. Logs MUST NOT contain credentials, tokens, or full payloads of authenticated requests/responses.

Metrics: each layer and each provider MUST expose at minimum:

request counts, error counts, latency histograms

rate-limit events

circuit-breaker state changes

ingestion lag (received_at vs. processed_at)

data-quality counters (gaps, duplicates, rejects)

Metric names MUST be stable and documented.

Tracing: cross-layer spans MUST be emitted with correlation IDs so a single request/event can be followed end-to-end without reading application code.

Health & readiness: each deployable component MUST expose distinct liveness and readiness signals, with readiness reflecting dependency availability.

Observability data MUST NOT itself leak secrets. This is a hard rule.

Observability requirements apply to both code and non-code artifacts (e.g., CI jobs and containers MUST emit structured status).

20. Definition of Ready (DoR)
A task is NOT ready for implementation until all of the following hold:

The task maps to exactly one primary responsibility (clause 10).

The architectural layer and frozen-tree path are identified.

The relevant contract(s) from the Registry (clause 14) are named and versioned.

Allowed and forbidden dependency directions for the task are stated.

Test scope is declared up-front, including the 100% coverage intent (clause 11) and any integration/E2E classification.

External dependencies (providers, libraries) are verified as available, with the capability matrix checked (clause 7).

Security classification of the task is stated (does it touch secrets, credentials, auth, or PII?).

Non-goals for the task are stated explicitly.

Rollback / removal path is stated if the task changes a contract.

If any DoR item is missing, the task is NOT READY and MUST NOT enter implementation. This complements — and does not replace — the Definition of Done already established by the Kit.

21. Non-Goals (Explicit Scope Exclusions)
The following are explicitly OUT OF SCOPE for this system unless the frozen architecture is formally amended:

High-frequency trading (HFT) / co-located / microsecond-latency strategies. The system targets correctness, integrity, and traceability — not latency races.

Custody, wallet management, or private-key handling of user funds.

Acting as a broker, dealer, or licensed financial intermediary.

Tax reporting, regulatory filing, or jurisdiction-specific compliance reporting on behalf of end users.

Providing investment advice or discretionary portfolio management.

Storing or processing end-user PII beyond what is strictly required for authenticated API access, and never in logs.

Building a proprietary exchange simulator that pretends to be a live provider. Simulation MUST be clearly labeled and isolated.

Introducing new top-level directories or new top-level architectural concepts into the frozen tree without an explicit unfreeze decision.

Non-goals are recorded here to prevent scope creep. Any proposal that falls into a non-goal MUST be raised as an explicit architecture change request, not implemented opportunistically.

22. Rate Limit Registry
Rate limiting is mandatory (Kit clause 6). This clause defines how it is sourced, applied, and verified.

Rules:

A central Rate Limit Registry MUST exist and MUST be the single source of truth for provider rate limits. The Registry location MUST follow the frozen tree; no new top-level directory may be created for it.

For each provider, the Registry MUST record:

REST endpoint-class limits (per endpoint family where relevant)

WebSocket connection limits and subscription limits

Order-placement / cancel limits if distinct from data limits

Weighted vs. simple counting model

Burst allowance, if any

Rate-limit response semantics (status code, headers, retry-after)

Documented source (official provider documentation URL + date)

Limits MUST be treated as verifiable facts, not assumptions. Each entry MUST cite its source and review date.

Runtime MUST respect dynamic signals (e.g., Retry-After, remaining-weight headers) in addition to static limits.

Rate limiters MUST be per-provider and per-endpoint-class; a single global limiter is insufficient.

HTTP 429 and equivalent provider signals MUST trigger exponential backoff with jitter and MUST be observable (clause 19).

Tests MUST cover: allowed request, throttled request, burst handling, dynamic-limit response, and recovery after backoff.

When a provider changes its published limits, the Registry MUST be updated and a compliance re-check MUST be performed before the next release (see clause 17).

23. Data Retention & Privacy
Data retention and privacy MUST be explicit, not accidental.

Rules:

Every category of stored data MUST have a declared retention period and a declared purpose.

Categories include at minimum: raw provider payloads, normalized market data, orders/fills, logs, metrics, error records, and any cached credentials material (which SHOULD NOT exist — credentials must come from secret management per Kit clause 6).

Raw payloads, if stored, MUST be immutable and hash-referenced per clause 16. Retention of raw payloads MUST be the shortest duration consistent with traceability and debugging needs.

Logs MUST NOT contain: API keys, secrets, tokens, full auth headers, or full user identifiers. Masking is enforced at the logging boundary (clause 19), not left to callers.

PII MUST NOT be stored unless strictly required, and where required it MUST be minimized, access-controlled, and auditable.

Deletion MUST be real: retention expiry MUST actually remove or irreversibly anonymize the data, not merely mark it hidden.

Any external export of data (analytics, third-party tools, backups) MUST be documented and MUST respect the same retention and privacy rules. Provider credentials MUST NOT be exported under any circumstance.

Backups inherit the retention policy of the source data.

Retention and deletion behavior MUST be testable where a runtime component owns that behavior. Where retention is enforced by infrastructure (e.g., storage lifecycle), that enforcement MUST be documented as a non-code gate per Kit clause 12.


═══════════════════════════════════════════════════════════════════════
APPENDIX B — MODERN ENGINEERING STANDARDS (ADDITIVE ONLY)
Status : ADDITIVE ONLY — no existing clause removed or modified
═══════════════════════════════════════════════════════════════════════

24. Global modern coding standard
All Python implementation MUST follow modern, internationally accepted
engineering standards, in addition to clauses 1–23. At minimum:

  • Adherence to PEP 8 (style), PEP 20 (Zen), PEP 484/604/695 (typing),
    PEP 257 (docstrings).
  • Use of modern Python 3.13+ syntax and idioms (match/case, type
    parameter syntax, typing.Self, ExceptionGroup, asyncio.TaskGroup).
  • Application of recognized design principles where they serve the
    frozen architecture: Single Responsibility, Separation of Concerns,
    Dependency Inversion at architectural boundaries, Explicit over
    Implicit.
  • Prefer composition over inheritance unless inheritance expresses a
    true is-a relationship required by the frozen tree.
  • Avoid deprecated APIs, dead code, magic values, hidden global state,
    and silent failures.
  • Naming MUST be explicit, meaningful, and consistent across layers.
  • All public APIs MUST be fully typed and documented.

Rules:
  • "Modern" MUST NOT be interpreted as permission to introduce new
    top-level directories, new architectural concepts, or to bypass the
    frozen tree (see clause 21).
  • "Modern" MUST NOT override any existing clause (1–23). In case of
    conflict, the earlier clause prevails.
  • Any modernization that changes a contract MUST go through clause 17
    (Contract Evolution Policy).
═══════════════════════════════════════════════════════════════════════
