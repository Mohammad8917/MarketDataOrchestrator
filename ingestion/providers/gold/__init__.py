"""Package boundary for gold ingestion providers.

FILE NAME     : ingestion/providers/gold/__init__.py
KIT ADDRESS   : github.com/Mohammad8917/MarketDataOrchestrator
VERSION       : 1.0.0
DATE          : 1405/07/02 — 2026-09-24
AUTHOR        : محمد حسن زاده
RESPONSIBILITY: Define the Python package boundary for gold-specific ingestion providers.
DEPENDENCIES  : None declared in current skeleton implementation.
PYTHON        : 3.13+
LAYER         : ingestion/providers/gold
DEPENDENCY DIRECTION: Gold providers depend inward on canonical ingestion provider contracts, not downstream layers.
OWNS          : Gold-provider package namespace and boundary.
DOES NOT OWN  : Shared provider contracts, normalization policy, analysis, strategy, decision, risk.
ALLOWED       : ingestion/interfaces provider contracts and approved transport/error abstractions when implemented.
FORBIDDEN     : analysis, indicators, strategy, decision, risk, persistence, concrete downstream consumers.
TEST SCOPE    : Package import/boundary integrity; no executable provider behavior is currently declared.
LICENSE       : Proprietary — All Rights Reserved
UNAUTHORIZED USE IS STRICTLY PROHIBITED.
PROJECT COMPLIANCE REFERENCE: Architecture Frozen v1.0 / Compliance Kit.
"""

# Frozen package boundary; provider implementation is intentionally deferred.
