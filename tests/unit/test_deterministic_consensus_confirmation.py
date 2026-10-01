"""FILE: tests/unit/test_deterministic_consensus_confirmation.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic directional consensus confirmation methodology.
LAYER: tests
OWNS: Methodology-level behavior verification.
DOES_NOT_OWN: trading profitability, provider behavior, risk, decision finalization
DEPENDENCIES: composition.deterministic_consensus; composition.confirmation_contract
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from math import inf, nan

import pytest

from composition.confirmation_contract import ConfirmationRequest
from composition.deterministic_consensus import (
    CONFIRMATION_METHODOLOGY_ID,
    CONFIRMATION_METHODOLOGY_VERSION,
    CONFIRMATION_THRESHOLD,
    DeterministicDirectionalConsensus,
)


def _request(signals: dict[str, float]) -> ConfirmationRequest:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return ConfirmationRequest(
        signals=signals,
        event_time=timestamp,
        received_at=timestamp,
        source_event_id="event-1",
    )


def test_methodology_metadata_is_stable() -> None:
    assert CONFIRMATION_METHODOLOGY_ID == "deterministic_directional_consensus_v1"
    assert CONFIRMATION_METHODOLOGY_VERSION == "1.0.0"
    assert CONFIRMATION_THRESHOLD == 0.5


@pytest.mark.parametrize(
    ("signals", "expected_score", "expected_confirmed"),
    [
        ({"a": 1.0, "b": 0.5, "c": -0.2, "d": 0.0}, 0.25, False),
        ({"a": 1.0, "b": 0.2, "c": 0.0}, 2 / 3, True),
        ({"a": -1.0, "b": -0.2, "c": 0.0}, -2 / 3, True),
        ({"a": 1.0, "b": 0.2, "c": -0.1, "d": -0.1}, 0.0, False),
        ({"a": 0.0, "b": 0.0}, 0.0, False),
    ],
)
def test_directional_consensus(
    signals: dict[str, float], expected_score: float, expected_confirmed: bool
) -> None:
    output = DeterministicDirectionalConsensus().confirm(_request(signals))
    assert output.score == pytest.approx(expected_score)
    assert output.confirmed is expected_confirmed


@pytest.mark.parametrize(
    "signals", [{}, {"a": nan}, {"a": inf}, {"a": -inf}, {"a": 1.1}, {"a": -1.1}]
)
def test_rejects_invalid_evidence(signals: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        DeterministicDirectionalConsensus().confirm(_request(signals))


def test_confirmation_id_is_deterministic_and_provenance_bound() -> None:
    output = DeterministicDirectionalConsensus().confirm(_request({"a": 1.0, "b": 1.0}))
    assert output.confirmation_id == "event-1:deterministic_directional_consensus_v1"
    assert output.event_time == datetime(2026, 1, 1, tzinfo=timezone.utc)
