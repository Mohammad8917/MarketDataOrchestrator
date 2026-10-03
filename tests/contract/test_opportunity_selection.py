"""Contract tests for the opportunity selection boundary."""

from datetime import datetime, timezone

import pytest

from shared.contracts.market_context import MarketContext
from shared.contracts.opportunity_ranking import OpportunityRankingOutput
from shared.contracts.opportunity_selection import OpportunitySelectionOutput


def _time() -> datetime:
    return datetime(2026, 10, 2, tzinfo=timezone.utc)


def _context() -> MarketContext:
    return MarketContext(
        market="Crypto",
        symbol="BTCUSDT",
        timeframe="1h",
        event_time=_time(),
        source_event_id="event-1",
    )


def _ranking() -> OpportunityRankingOutput:
    return OpportunityRankingOutput(
        eligible=True,
        action="BUY",
        rank_score=0.8,
        event_time=_time(),
        ranking_id="rank-1",
        source_safety_id="safety-1",
        source_edge_id="edge-1",
    )


def test_selection_accepts_valid_output() -> None:
    output = OpportunitySelectionOutput(
        selected=(_ranking(),),
        selection_id="selection-1",
        market_context=_context(),
    )
    assert output.selected[0].ranking_id == "rank-1"


@pytest.mark.parametrize("value", ["not-a-tuple", None, 1])
def test_selection_rejects_invalid_selected_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="selected must be a tuple"):
        OpportunitySelectionOutput(
            selected=value,  # type: ignore[arg-type]
            selection_id="selection-1",
            market_context=_context(),
        )


@pytest.mark.parametrize("value", [0, None, object()])
def test_selection_rejects_invalid_selection_id_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="selection_id must be a string"):
        OpportunitySelectionOutput(
            selected=(_ranking(),),
            selection_id=value,  # type: ignore[arg-type]
            market_context=_context(),
        )


@pytest.mark.parametrize("value", [0, None, object()])
def test_selection_rejects_invalid_market_context_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="market_context must be a MarketContext"):
        OpportunitySelectionOutput(
            selected=(_ranking(),),
            selection_id="selection-1",
            market_context=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("value", [None, 0, object()])
def test_selection_rejects_invalid_contract_version_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="contract_version must be a string"):
        OpportunitySelectionOutput(
            selected=(_ranking(),),
            selection_id="selection-1",
            market_context=_context(),
            contract_version=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("version", ["", "   ", "\t", "\n"])
def test_selection_rejects_blank_contract_version(version: str) -> None:
    with pytest.raises(ValueError, match="contract_version must not be empty"):
        OpportunitySelectionOutput(
            selected=(_ranking(),),
            selection_id="selection-1",
            market_context=_context(),
            contract_version=version,
        )


@pytest.mark.parametrize("version", ["2.0.0", "0.9.0", "unknown"])
def test_selection_rejects_unsupported_contract_version(version: str) -> None:
    with pytest.raises(ValueError, match="unsupported contract_version"):
        OpportunitySelectionOutput(
            selected=(_ranking(),),
            selection_id="selection-1",
            market_context=_context(),
            contract_version=version,
        )


def test_selection_rejects_duplicate_ranking_identity() -> None:
    ranking = _ranking()
    with pytest.raises(ValueError, match="selected ranking_id values must be unique"):
        OpportunitySelectionOutput(
            selected=(ranking, ranking),
            selection_id="selection-1",
            market_context=_context(),
        )


def _ranking_with(
    *,
    rank_score: float = 0.8,
    ranking_id: str = "rank-1",
    eligible: bool = True,
    event_time: datetime | None = None,
) -> OpportunityRankingOutput:
    return OpportunityRankingOutput(
        eligible=eligible,
        action="BUY",
        rank_score=rank_score,
        event_time=event_time or _time(),
        ranking_id=ranking_id,
        source_safety_id="safety-1",
        source_edge_id="edge-1",
    )


@pytest.mark.parametrize("value", ["", "   ", "\t", "\n"])
def test_selection_rejects_blank_selection_id(value: str) -> None:
    with pytest.raises(ValueError, match="selection_id must not be empty"):
        OpportunitySelectionOutput(
            selected=(_ranking(),),
            selection_id=value,
            market_context=_context(),
        )


def test_selection_rejects_non_exact_ranking_type() -> None:
    class DerivedRanking(OpportunityRankingOutput):
        pass

    ranking = DerivedRanking(
        eligible=True,
        action="BUY",
        rank_score=0.8,
        event_time=_time(),
        ranking_id="rank-derived",
        source_safety_id="safety-1",
        source_edge_id="edge-1",
    )
    with pytest.raises(ValueError, match="selected must contain only OpportunityRankingOutput values"):
        OpportunitySelectionOutput(
            selected=(ranking,),
            selection_id="selection-1",
            market_context=_context(),
        )


def test_selection_rejects_ineligible_opportunity() -> None:
    with pytest.raises(ValueError, match="eligible opportunities only"):
        OpportunitySelectionOutput(
            selected=(_ranking_with(eligible=False),),
            selection_id="selection-1",
            market_context=_context(),
        )


def test_selection_rejects_descending_rank_score() -> None:
    with pytest.raises(ValueError, match="ordered by rank_score"):
        OpportunitySelectionOutput(
            selected=(
                _ranking_with(rank_score=0.5, ranking_id="rank-1"),
                _ranking_with(rank_score=0.8, ranking_id="rank-2"),
            ),
            selection_id="selection-1",
            market_context=_context(),
        )


def test_selection_rejects_event_time_mismatch() -> None:
    with pytest.raises(ValueError, match="event_time must match market context"):
        OpportunitySelectionOutput(
            selected=(_ranking_with(event_time=datetime(2026, 10, 3, tzinfo=timezone.utc)),),
            selection_id="selection-1",
            market_context=_context(),
        )
