"""FILE: tests/unit/test_mtf_structure_replay.py
RESPONSIBILITY: Verify deterministic MTF structure replay consumer invariants.
"""

from datetime import datetime, timezone

import pytest

from backtest.mtf_structure_replay import MtfStructureReplay
from shared.contracts.market_structure import MarketStructureOutput
from shared.contracts.mtf_structure import (
    MtfStructureInput,
    MtfStructureObservation,
    MtfStructureOutput,
    MtfStructureRequest,
)


def _request(event_time: datetime, source_event_id: str) -> MtfStructureRequest:
    structure = MarketStructureOutput(
        points=(),
        events=(),
        state=None,
        event_time=event_time,
        source_event_id=f"{source_event_id}-structure",
        contract_version="1.0.0",
    )
    return MtfStructureRequest(
        inputs=(MtfStructureInput("1h", structure),),
        event_time=event_time,
        received_at=event_time,
        source_event_id=source_event_id,
    )


class _Evaluator:
    contract_id = "mtf_structure_alignment_boundary"
    contract_version = "1.0.0"

    def __init__(self) -> None:
        self.requests: list[MtfStructureRequest] = []

    def evaluate(self, request: MtfStructureRequest) -> MtfStructureOutput:
        self.requests.append(request)
        return MtfStructureOutput(
            observations=(MtfStructureObservation("1h", "bullish"),),
            alignment="bullish",
            event_time=request.event_time,
            source_event_id=request.source_event_id,
        )


def test_replays_in_order_and_returns_immutable_results() -> None:
    first = _request(datetime(2026, 1, 1, tzinfo=timezone.utc), "e1")
    second = _request(datetime(2026, 1, 2, tzinfo=timezone.utc), "e2")
    evaluator = _Evaluator()

    output = MtfStructureReplay().run((first, second), evaluator)

    assert output.results[0].event_time < output.results[1].event_time
    assert tuple(evaluator.requests) == (first, second)
    with pytest.raises(AttributeError):
        output.results = ()  # type: ignore[misc]


def test_rejects_empty_requests() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        MtfStructureReplay().run((), _Evaluator())


def test_rejects_non_increasing_requests() -> None:
    request = _request(datetime(2026, 1, 1, tzinfo=timezone.utc), "e1")
    with pytest.raises(ValueError, match="strictly ordered"):
        MtfStructureReplay().run((request, request), _Evaluator())


def test_rejects_evaluator_without_contract_protocol() -> None:
    class Invalid:
        pass

    request = _request(datetime(2026, 1, 1, tzinfo=timezone.utc), "e1")
    with pytest.raises(TypeError, match="implement"):
        MtfStructureReplay().run((request,), Invalid())  # type: ignore[arg-type]


def test_rejects_output_provenance_mismatch() -> None:
    request = _request(datetime(2026, 1, 1, tzinfo=timezone.utc), "e1")

    class InvalidOutput(_Evaluator):
        def evaluate(self, request: MtfStructureRequest) -> MtfStructureOutput:
            return MtfStructureOutput(
                observations=(MtfStructureObservation("1h", "bullish"),),
                alignment="bullish",
                event_time=request.event_time,
                source_event_id="wrong",
            )

    with pytest.raises(ValueError, match="source_event_id"):
        MtfStructureReplay().run((request,), InvalidOutput())
