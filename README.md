# MarketDataOrchestrator

Architecture Frozen v1.0.

Layered, event-driven market-data and analysis orchestrator for Crypto, Forex, and Gold.

The repository structure is intentionally frozen. Implementation must preserve the documented layer boundaries, contracts, temporal integrity, traceability, and validation ownership.

## 🔴 MANDATORY KIT ENTRY GATE

**Every time the MarketDataOrchestrator Compliance Kit is opened, the first action MUST be to check this Compliance Kit before doing anything else.**

This is a mandatory precondition for all work on this repository.

Required order:

**ENTER KIT → CHECK COMPLIANCE KIT → VERIFY REQUEST AGAINST KIT → ONLY THEN PROCEED**

Before any analysis, design, code generation, file modification, commit, or repository change:

1. Re-check the current **Architecture & Implementation Compliance Kit**.
2. Verify the requested work against its rules, frozen repository tree, layer boundaries, dependency rules, contracts, invariants, and Definition of Done.
3. Only after that check may implementation or repository changes proceed.

**This check must be performed again on every new entry into the Kit, even if it was checked earlier in the same conversation, task, or project.**

No implementation work may bypass this gate.

## 🔴 CODING STANDARDS & COMPLIANCE — MANDATORY

**Owner / Author:** محمد حسن زاده  
**License policy:** Proprietary — All Rights Reserved  
**Target runtime:** Python 3.13+  
**Exchange integration target:** 15 exchanges, subject to provider/API capability verification.

### 1. Mandatory source-file header

Before writing or modifying executable Python code in this repository, the file MUST begin with a project-compliance header containing, at minimum:

- file name
- Kit/repository address
- file SemVer
- Persian and Gregorian date
- author: محمد حسن زاده
- responsibility of the file
- direct dependencies and versions
- Python compatibility: 3.13+
- proprietary/all-rights-reserved notice
- unauthorized-use warning
- project compliance reference

The header must also identify the file's architectural responsibility and its direct dependencies so that ownership and dependency direction are visible from the file itself.

For Python files, the header must remain valid Python syntax (normally a module docstring). Non-Python files must use the native comment/documentation syntax appropriate to that file type.

### 2. Unauthorized-use notice

Project source files may contain a notice that unauthorized copying, redistribution, modification, reverse engineering, sale, or other use without written authorization is prohibited.

Any reference to legal enforcement must be treated as a **project legal notice, not a substitute for legal advice**, and must not assert that a particular remedy is guaranteed. Applicable rights and remedies depend on the governing law and the facts of the case.

**Owner:** محمد حسن زاده.

### 3. Version and date

Every newly written or materially modified source file must carry its own SemVer file version and date in its header.

Repository-level release versioning remains governed by the project's SemVer policy, VERSION, CHANGELOG, and Git tags.

### 4. Python compatibility

New Python implementation MUST target Python **3.13+** and use modern typing and asyncio facilities where appropriate.

Compatibility claims must be verified by CI rather than assumed. Code must not rely on APIs removed or deprecated for the declared target without an explicit compatibility decision.

### 5. Architecture ownership and dependencies

Every implementation file must state:

- its single primary responsibility;
- its direct dependencies;
- the architectural layer/subsystem it belongs to;
- any important dependency-direction constraint.

No file may silently cross the frozen layer boundaries.

### 6. Async-first and security requirements

For exchange/network integrations:

- async-first design is mandatory;
- blocking I/O is forbidden on the event loop;
- secrets must come only from environment/secret-management infrastructure;
- secrets must never be committed or logged;
- rate limiting is mandatory;
- HTTP 429 handling requires exponential backoff;
- exchange failures require contextual, secret-safe errors;
- exchange connectors require isolation behind shared interfaces.

### 7. Exchange integration target

The system target is integration capability for at least these 15 exchanges:

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

Each integration must conform to the project's shared provider contract and must not leak exchange-specific implementation details into domain, analysis, decision, risk, or other prohibited layers.

Actual REST/WebSocket/Testnet availability must be verified against current official exchange/provider documentation before implementation or release; capabilities must not be represented as available when the upstream service does not support them.

### 8. Testing and quality gates

New implementation is expected to satisfy:

- complete type hints;
- docstrings for public classes/functions/methods;
- Ruff/flake8-compatible linting policy;
- mypy-compatible type checking;
- pytest + pytest-asyncio tests where async behavior exists;
- mocked exchange calls in tests;
- minimum project coverage target of 80%;
- architecture and dependency tests;
- CI verification before merge.

### 9. Review workflow

Implementation follows:

**DRAFT → SELF-REVIEW → PEER-REVIEW → APPROVED → RELEASED**

No implementation should be treated as released merely because it exists in the working tree.

## ⚠️ Frozen-tree compatibility note

The repository's previously frozen Architecture v1.0 tree is authoritative for physical paths. The user-provided generic project_root/exchanges/, strategies/, LICENSE, and requirements.txt layout is therefore **not** adopted as a new directory structure.

The existing architecture maps exchange integrations under:

ingestion/interfaces/  
ingestion/providers/  
domain_adapters/

and strategy implementation under:

strategy/

This preserves the repository's existing layer contracts and avoids introducing duplicate architecture.

Likewise, the legal/ownership requirements above are recorded as project policy; a separate LICENSE file is not added because it is outside the currently frozen tree unless the tree is explicitly unfrozen.

## 🔐 Security baseline

API keys, secrets, passwords, tokens, and private credentials MUST NOT appear in source code, logs, commits, test fixtures, or error messages.

Sensitive configuration must be externalized. Logging must mask sensitive values. Exchange credentials must never be sent to third parties except the intended provider/API endpoint and only as required by the provider contract.

## 📌 Compliance rule for future coding

Before **every** coding change:

**ENTER KIT → CHECK COMPLIANCE KIT → VERIFY REQUEST AGAINST KIT → ONLY THEN PROCEED**

If the requested change conflicts with the frozen architecture, ownership boundaries, security policy, provider contracts, or another mandatory rule, implementation must stop and the conflict must be reported before code is produced.

### 10. Per-file single-responsibility invariant

Every Python source file MUST declare **exactly one primary responsibility** in its header using the `RESPONSIBILITY` field. The declared responsibility must match the architectural role of the file and must not combine unrelated responsibilities.

A file may contain multiple functions, methods, or classes only when they are cohesive implementation elements of that one primary responsibility. Independent responsibilities MUST NOT be co-located merely because they belong to the same layer or subsystem.

Every Python source file MUST also declare its current direct dependency state in the `DEPENDENCIES` field. Direct dependencies MUST reflect actual imports/calls/resources rather than inferred or generic descriptions. Architectural permissions and prohibitions are separate concerns and MUST NOT be represented as if they were current runtime dependencies.

This invariant applies to all 457 Python files currently present in the repository, including package markers, application/core files, domain layers, indicators, tests, and shared contracts.

### 11. Per-file test and 100% coverage acceptance gate

Every testable implementation file MUST have an explicit test scope and MUST be independently verifiable against its declared responsibility.

For every testable production Python file:

- **Statement coverage MUST be 100%.**
- **Branch coverage MUST be 100%.**
- All reachable success paths MUST be tested.
- All reachable failure and exception paths MUST be tested.
- Boundary, empty, invalid, and degraded-input behavior MUST be tested wherever the file's contract permits those states.
- Public behavior and contract boundaries MUST be verified, not merely executed.
- Async behavior MUST include cancellation, timeout, and relevant concurrency/error paths where applicable.
- External I/O MUST be isolated behind test doubles in unit tests unless the test is explicitly classified as integration/E2E.
- Tests MUST be deterministic and must not depend on live exchange services, credentials, uncontrolled wall-clock time, or uncontrolled randomness.
- Coverage exclusions and `pragma: no cover` MUST NOT be used to manufacture compliance. Any unavoidable exclusion requires an explicit architectural justification and separate review.
- 100% line coverage alone is **NOT sufficient** for acceptance.
- Mutation testing SHOULD be used for critical decision, risk, validation, and architecture logic; surviving mutations in critical logic are grounds for rejection until the test weakness is resolved.
- A file with missing tests, incomplete required paths, or coverage below 100% is **NOT COMPLIANT**.

The repository-wide historical target of 80% is superseded by this per-file acceptance gate. The 80% figure MUST NOT be used to approve an individual file that fails its 100% requirement.

### 12. File acceptance gate

A testable implementation file is accepted only when all mandatory gates pass:

`ONE FILE → ONE PRIMARY RESPONSIBILITY → EXPLICIT DEPENDENCIES → COMPLETE TEST CONTRACT → 100% REQUIRED COVERAGE → PASS`

If any mandatory gate fails, the file is **REJECTED** and MUST NOT be treated as production-ready or released.

Architecture tests, dependency-direction tests, contract tests, validation tests, and integration/E2E tests remain additional requirements; they do not replace the per-file 100% test requirement.

Non-code artifacts such as configuration, CI workflows, Dockerfiles, Makefiles, and scripts MUST use an appropriate structural/behavioral validation gate rather than falsely claiming Python line coverage.
