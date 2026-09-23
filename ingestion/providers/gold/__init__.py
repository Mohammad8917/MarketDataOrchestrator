"""Define the Python package boundary for ingestion/providers/gold.

FILE NAME     : ingestion/providers/gold/__init__.py
KIT ADDRESS   : github.com/Mohammad8917/MarketDataOrchestrator
VERSION       : 1.0.0
DATE          : 1405/07/02 — 2026-09-24
AUTHOR        : محمد حسن زاده
RESPONSIBILITY: Define the Python package boundary for ingestion/providers/gold.
DEPENDENCIES  : None declared in current skeleton implementation.
LAYER         : ingestion
DEPENDENCY DIRECTION: Ingestion is upstream: receive, normalize, validate, and expose canonical market data.
OWNS          : Only the single primary responsibility declared above, including its local invariants and contract behavior.
DOES NOT OWN  : analysis, indicators, strategy, decision, risk, persistence policy
ALLOWED ARCHITECTURAL DEPENDENCIES: shared, config, domain contracts, and ingestion interfaces
FORBIDDEN DEPENDENCIES: analysis, indicators, strategy, decision, risk, persistence policy
DEPENDENCY CYCLE POLICY: No dependency cycle. Allowed direction: Ingestion is upstream: receive, normalize, validate, and expose canonical market data. Downstream layers MUST NOT be imported back into ingestion.
TEST SCOPE    : 100% statement and branch coverage when executable; all success, failure, exception, boundary, invalid/degraded, timeout/cancellation/concurrency paths applicable to the contract. No live external I/O in unit tests; mutation testing for critical validation/decision/risk/architecture logic.
LICENSE       : Proprietary — All Rights Reserved
UNAUTHORIZED USE IS STRICTLY PROHIBITED.
PROJECT COMPLIANCE REFERENCE: Architecture Frozen v1.0 / Compliance Kit.
"""

# Frozen skeleton; executable implementation is intentionally deferred until its contract is implemented.
