"""Implement the stop loss risk responsibility at its declared risk subsystem boundary.

FILE NAME     : risk/stop_loss.py
KIT ADDRESS   : github.com/Mohammad8917/MarketDataOrchestrator
VERSION       : 1.0.0
DATE          : 1405/07/02 — 2026-09-24
AUTHOR        : محمد حسن زاده
RESPONSIBILITY: Implement the stop loss risk responsibility at its declared risk subsystem boundary.
DEPENDENCIES  : None declared in current skeleton implementation.
LAYER         : risk
DEPENDENCY DIRECTION: Perform independent risk assessment, sizing, limits, stop/take-profit policy, and risk validation.
OWNS          : Only the single primary responsibility declared above, including its local invariants and contract behavior.
DOES NOT OWN  : strategy selection, evidence generation, provider I/O, output delivery
ALLOWED ARCHITECTURAL DEPENDENCIES: decision, domain, shared risk contracts, approved configuration
FORBIDDEN DEPENDENCIES: strategy selection, evidence generation, provider I/O, output delivery
DEPENDENCY CYCLE POLICY: No dependency cycle. Allowed direction: Perform independent risk assessment, sizing, limits, stop/take-profit policy, and risk validation. Downstream layers MUST NOT be imported back into risk.
TEST SCOPE    : 100% statement and branch coverage when executable; all success, failure, exception, boundary, invalid/degraded, timeout/cancellation/concurrency paths applicable to the contract. No live external I/O in unit tests; mutation testing for critical validation/decision/risk/architecture logic.
LICENSE       : Proprietary — All Rights Reserved
UNAUTHORIZED USE IS STRICTLY PROHIBITED.
PROJECT COMPLIANCE REFERENCE: Architecture Frozen v1.0 / Compliance Kit.
"""

# Frozen skeleton; executable implementation is intentionally deferred until its contract is implemented.
