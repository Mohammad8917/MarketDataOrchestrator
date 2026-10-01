"""FILE: domain/market_scope.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the canonical three-market product scope.
LAYER: domain
OWNS: Market scope identity and immutable market-scope semantics.
DOES_NOT_OWN: provider transport, symbol normalization, persistence, analysis, strategy, risk, execution, or orchestration.
DEPENDENCIES: stdlib:enum
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from enum import StrEnum


class MarketScope(StrEnum):
    """Canonical product markets; no other market is in the v1 product scope."""

    CRYPTO = "crypto"
    FOREX = "forex"
    GOLD = "gold"


CANONICAL_MARKET_SCOPES = frozenset(MarketScope)


def is_canonical_market(value: MarketScope) -> bool:
    """Return whether value belongs to the locked three-market product scope."""
    return value in CANONICAL_MARKET_SCOPES
