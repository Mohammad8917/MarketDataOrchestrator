"""Define the Python package boundary for validation.

FILE NAME     : validation/__init__.py
KIT ADDRESS   : github.com/Mohammad8917/MarketDataOrchestrator
VERSION       : 1.0.0
DATE          : 1405/07/02 — 2026-09-24
AUTHOR        : محمد حسن زاده
RESPONSIBILITY: Define the Python package boundary for validation.
DEPENDENCIES  : None declared in current skeleton implementation.
LAYER         : validation
DEPENDENCY DIRECTION: Enforce pipeline, contract, temporal, evidence/decision/risk, and pre-signal gates.
OWNS          : Only the single primary responsibility declared above, including its local invariants and contract behavior.
DOES NOT OWN  : provider business logic, strategy generation, persistence mutation, output formatting
ALLOWED ARCHITECTURAL DEPENDENCIES: upstream canonical contracts including ingestion, evidence, decision, risk, shared
FORBIDDEN DEPENDENCIES: provider business logic, strategy generation, persistence mutation, output formatting
DEPENDENCY CYCLE POLICY: No dependency cycle. Allowed direction: Enforce pipeline, contract, temporal, evidence/decision/risk, and pre-signal gates. Downstream layers MUST NOT be imported back into validation.
TEST SCOPE    : 100% statement and branch coverage when executable; all success, failure, exception, boundary, invalid/degraded, timeout/cancellation/concurrency paths applicable to the contract. No live external I/O in unit tests; mutation testing for critical validation/decision/risk/architecture logic.
LICENSE       : Proprietary — All Rights Reserved
UNAUTHORIZED USE IS STRICTLY PROHIBITED.
PROJECT COMPLIANCE REFERENCE: Architecture Frozen v1.0 / Compliance Kit.
"""

# Frozen skeleton; executable implementation is intentionally deferred until its contract is implemented.
