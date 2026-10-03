"""Adversarial tests for MTF structure nested runtime boundaries."""

from datetime import datetime, timezone

import pytest

from shared.contracts.market_structure import MarketStructureOutput
from shared.contracts.mtf_structure import (
    MtfStructureInput,
    MtfStructureObservation,
    MtfStructureOutput,
    MtfStructureRequest,
)

_TIME = datetime(2026, 10, 3, tzinfo=timezone.utc)


def _structure() -> MarketStructureOutput:
    return MarketStructureOutput(
        points=(),
        events=(),
        state=None,
        event_time=_TIME,
        source_event_id="source-1",
    )


def test_input_rejects_invalid_nested_structure_type() -> None:
    with pytest.raises(ValueError, match="structure must be a MarketStructureOutput"):
        MtfStructureInput(timeframe="1H", structure=object())  # type: ignore[arg-type]


@pytest.mark.parametrize("inputs", [[MtfStructureInput("1H", _structure())], (object(),)])
def test_request_rejects_non_tuple_or_malformed_inputs(inputs: object) -> None:
    with pytest.raises(ValueError, match="(inputs must be a tuple|inputs must contain only)"):
        MtfStructureRequest(
            inputs=inputs,  # type: ignore[arg-type]
            event_time=_TIME,
            received_at=_TIME,
            source_event_id="source-1",
        )


@pytest.mark.parametrize("observations", [[MtfStructureObservation("1H", "bullish")], (object(),)])
def test_output_rejects_non_tuple_or_malformed_observations(observations: object) -> None:
    with pytest.raises(ValueError, match="(observations must be a tuple|observations must contain only)"):
        MtfStructureOutput(
            observations=observations,  # type: ignore[arg-type]
            alignment="bullish",
            event_time=_TIME,
            source_event_id="source-1",
        )


@pytest.mark.parametrize("version", ["", "   ", "\t", "\n", None, 0])
def test_output_rejects_invalid_contract_version(version: object) -> None:
    with pytest.raises(ValueError, match="contract_version (must be a string|must not be empty)"):
        MtfStructureOutput(
            observations=(MtfStructureObservation("1H", "bullish"),),
            alignment="bullish",
            event_time=_TIME,
            source_event_id="source-1",
            contract_version=version,  # type: ignore[arg-type]
        )
