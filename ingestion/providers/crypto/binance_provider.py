"""Binance-specific ingestion provider boundary.

FILE NAME     : ingestion/providers/crypto/binance_provider.py
KIT ADDRESS   : github.com/Mohammad8917/MarketDataOrchestrator
VERSION       : 1.0.0
DATE          : 1405/07/02 — 2026-09-24
AUTHOR        : محمد حسن زاده
RESPONSIBILITY: Adapt Binance market-data access into the canonical ingestion-provider boundary.
DEPENDENCIES  : None declared in current skeleton implementation.
PYTHON        : 3.13+
LAYER         : ingestion/providers/crypto
DEPENDENCY DIRECTION: Provider implementation may depend on ingestion/interfaces and approved transport/error infrastructure; downstream layers must depend on contracts, never this concrete provider.
OWNS          : Binance-specific transport/protocol adaptation and provider-boundary error translation once implemented.
DOES NOT OWN  : Canonical provider contracts, normalization, indicators, analysis, strategy, decision, risk, persistence.
ALLOWED       : ingestion/interfaces/market_provider.py and approved transport, configuration, rate-limit, circuit-breaker, and error abstractions when actually implemented.
FORBIDDEN     : Direct dependencies on analysis, indicators, strategy, decision, risk, persistence, or downstream application behavior.
TEST SCOPE    : Contract success/rejection paths, timeout, cancellation, rate-limit/429, provider failure, malformed upstream data, isolation and retry boundaries when implemented; external I/O must be mocked in unit tests.
LICENSE       : Proprietary — All Rights Reserved
UNAUTHORIZED USE IS STRICTLY PROHIBITED.
PROJECT COMPLIANCE REFERENCE: Architecture Frozen v1.0 / Compliance Kit.
"""

# Frozen provider skeleton; Binance integration is intentionally deferred.
