"""FILE: tests/unit/analysis/structure/test_market_structure.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic market-structure evaluator composition and point-in-time output behavior.
LAYER: tests
OWNS: Evaluator acceptance tests for the market-structure analysis boundary.
DOES_NOT_OWN: methodology invention, provider transport, persistence, strategy, or risk.
DEPENDENCIES: pytest, datetime, decimal, analysis.structure.market_structure, shared.contracts.market_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock

from analysis.structure.market_structure import DeterministicMarketStructureEvaluator
from shared.contracts.market_structure import (
    MARKET_STRUCTURE_CONTRACT_ID,
    MARKET_STRUCTURE_CONTRACT_VERSION,
    MarketStructureBar,
    MarketStructureRequest,
)


def _bar(index: int, high: int, low: int, close: int) -> MarketStructureBar:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=index)
    return MarketStructureBar(
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"bar-{index}",
        open=Decimal(str(close)),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(close)),
        volume=Decimal("1"),
    )


def _request() -> MarketStructureRequest:
    bars = (
        _bar(0, 10, 8, 9),
        _bar(1, 11, 7, 10),
        _bar(2, 12, 6, 11),
        _bar(3, 11, 7, 10),
        _bar(4, 10, 8, 9),
        _bar(5, 13, 9, 13),
        _bar(6, 12, 9, 11),
        _bar(7, 11, 9, 10),
    )
    return MarketStructureRequest(
        bars=bars,
        event_time=bars[-1].event_time,
        received_at=bars[-1].received_at,
        source_event_id=bars[-1].source_event_id,
    )


def test_evaluator_exposes_contract_identity() -> None:
    evaluator = DeterministicMarketStructureEvaluator()
    assert evaluator.contract_id == MARKET_STRUCTURE_CONTRACT_ID
    assert evaluator.contract_version == MARKET_STRUCTURE_CONTRACT_VERSION


def test_evaluator_composes_labels_and_break_events() -> None:
    output = DeterministicMarketStructureEvaluator().evaluate(_request())

    assert [(point.kind, point.price_level) for point in output.points] == [
        ("HH", Decimal("13")),
    ]
    assert [(event.kind, event.reference_price) for event in output.events] == [
        ("breakout", Decimal("12")),
    ]
    assert output.event_time == datetime(2026, 1, 1, 0, 7, tzinfo=UTC)
    assert output.source_event_id == "bar-7"


def test_evaluator_does_not_invent_state_classification() -> None:
    output = DeterministicMarketStructureEvaluator().evaluate(_request())
    assert output.state is None


def test_evaluator_does_not_emit_unconfirmed_final_pivot() -> None:
    bars = (
        _bar(0, 10, 8, 9),
        _bar(1, 11, 7, 10),
        _bar(2, 12, 6, 11),
        _bar(3, 11, 7, 10),
        _bar(4, 10, 8, 9),
    )
    request = MarketStructureRequest(
        bars=bars,
        event_time=bars[-1].event_time,
        received_at=bars[-1].received_at,
        source_event_id=bars[-1].source_event_id,
    )

    output = DeterministicMarketStructureEvaluator().evaluate(request)

    assert all(point.event_time <= request.event_time for point in output.points)
    assert all(event.event_time <= request.event_time for event in output.events)


def test_evaluator_delegates_exact_request_bars_to_injected_components() -> None:
    swing_detector = Mock()
    labeler = Mock()
    break_detector = Mock()
    swing_detector.detect.return_value = ()
    labeler.label.return_value = ()
    break_detector.detect.return_value = ()
    request = _request()

    output = DeterministicMarketStructureEvaluator(
        swing_detector=swing_detector,
        labeler=labeler,
        break_detector=break_detector,
    ).evaluate(request)

    swing_detector.detect.assert_called_once_with(request.bars)
    labeler.label.assert_called_once_with(())
    break_detector.detect.assert_called_once_with(request.bars, ())
    assert output.points == ()
    assert output.events == ()
    assert output.state is None
