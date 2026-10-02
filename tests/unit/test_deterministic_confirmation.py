"""FILE: tests/unit/test_deterministic_confirmation.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic majority confirmation behavior and identity.
LAYER: tests
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import UTC, datetime

import pytest

from composition.confirmation_contract import ConfirmationRequest
from composition.deterministic_confirmation import DeterministicMajorityConfirmation


NOW = datetime(2026, 10, 2, 9, tzinfo=UTC)


def request(signals: dict[str, float]) -> ConfirmationRequest:
    return ConfirmationRequest(
        signals=signals,
        event_time=NOW,
        received_at=NOW,
        source_event_id="evt-1",
    )


def test_confirms_directional_majority() -> None:
    result = DeterministicMajorityConfirmation().confirm(
        request({"trend": 1.0, "momentum": 1.0, "structure": -1.0})
    )

    assert result.confirmed is True
    assert result.score == pytest.approx(1 / 3)
    assert result.event_time == NOW


def test_rejects_tie_and_returns_neutral_score() -> None:
    result = DeterministicMajorityConfirmation().confirm(
        request({"trend": 1.0, "momentum": -1.0})
    )

    assert result.confirmed is False
    assert result.score == 0.0


def test_requires_minimum_active_signals() -> None:
    result = DeterministicMajorityConfirmation().confirm(
        request({"trend": 1.0, "momentum": 0.0, "structure": 0.0})
    )

    assert result.confirmed is False
    assert result.score == 0.0


def test_confirmation_identity_is_deterministic() -> None:
    evaluator = DeterministicMajorityConfirmation()
    signals = {"momentum": 1.0, "trend": -1.0, "structure": 1.0}

    first = evaluator.confirm(request(signals))
    second = evaluator.confirm(request(dict(reversed(tuple(signals.items())))))

    assert first.confirmation_id == second.confirmation_id
    assert len(first.confirmation_id) == 64


@pytest.mark.parametrize("agreement", (0.0, 1.1))
def test_rejects_invalid_agreement(agreement: float) -> None:
    with pytest.raises(ValueError, match="minimum_agreement"):
        DeterministicMajorityConfirmation(minimum_agreement=agreement)


def test_rejects_invalid_signal_count() -> None:
    with pytest.raises(ValueError, match="minimum_active_signals"):
        DeterministicMajorityConfirmation(minimum_active_signals=1)
