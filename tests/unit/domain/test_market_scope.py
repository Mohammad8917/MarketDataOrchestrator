"""Contract tests for the canonical three-market product scope."""

from domain.market_scope import CANONICAL_MARKET_SCOPES, MarketScope, is_canonical_market


def test_canonical_scope_contains_exactly_three_markets() -> None:
    assert CANONICAL_MARKET_SCOPES == {
        MarketScope.CRYPTO,
        MarketScope.FOREX,
        MarketScope.GOLD,
    }


def test_market_values_are_stable_machine_identifiers() -> None:
    assert MarketScope.CRYPTO.value == "crypto"
    assert MarketScope.FOREX.value == "forex"
    assert MarketScope.GOLD.value == "gold"


def test_only_canonical_market_scope_values_are_accepted() -> None:
    for market in MarketScope:
        assert is_canonical_market(market)


def test_unknown_string_is_not_a_market_scope_member() -> None:
    assert "stocks" not in CANONICAL_MARKET_SCOPES
    assert "commodities" not in CANONICAL_MARKET_SCOPES
