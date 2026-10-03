from datetime import datetime, timezone

import pytest

from shared.contracts.pretrade_safety import PreTradeSafetyOutput


EVENT_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


@pytest.mark.parametrize("value", ["2026-01-01T00:00:00Z", 0, None])
def test_rejects_invalid_event_time_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        PreTradeSafetyOutput(
            approved=False,
            action="NO_TRADE",
            exposure_fraction=0.0,
            reasons=("RISK_REJECTED",),
            event_time=value,  # type: ignore[arg-type]
            safety_id="safety-1",
        )


@pytest.mark.parametrize("value", ["0.5", True, None, float("nan"), float("inf")])
def test_rejects_invalid_exposure_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="exposure_fraction must be (numeric|finite and between)"):
        PreTradeSafetyOutput(
            approved=False,
            action="NO_TRADE",
            exposure_fraction=value,  # type: ignore[arg-type]
            reasons=("RISK_REJECTED",),
            event_time=EVENT_TIME,
            safety_id="safety-1",
        )


@pytest.mark.parametrize("value", [0, None, object()])
def test_rejects_invalid_action_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="action must be a string"):
        PreTradeSafetyOutput(
            approved=False,
            action=value,  # type: ignore[arg-type]
            exposure_fraction=0.0,
            reasons=("RISK_REJECTED",),
            event_time=EVENT_TIME,
            safety_id="safety-1",
        )


@pytest.mark.parametrize("value", [0, None, object()])
def test_rejects_invalid_safety_id_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="safety_id must be a string"):
        PreTradeSafetyOutput(
            approved=False,
            action="NO_TRADE",
            exposure_fraction=0.0,
            reasons=("RISK_REJECTED",),
            event_time=EVENT_TIME,
            safety_id=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("value", [[], ["RISK_REJECTED"], None])
def test_rejects_invalid_reasons_container_runtime_types(value: object) -> None:
    if isinstance(value, tuple):
        pytest.skip("valid control")
    with pytest.raises(ValueError, match="reasons must be a tuple"):
        PreTradeSafetyOutput(
            approved=False,
            action="NO_TRADE",
            exposure_fraction=0.0,
            reasons=value,  # type: ignore[arg-type]
            event_time=EVENT_TIME,
            safety_id="safety-1",
        )


def test_rejects_invalid_reason_runtime_types() -> None:
    with pytest.raises(ValueError, match="reasons must contain only strings"):
        PreTradeSafetyOutput(
            approved=False,
            action="NO_TRADE",
            exposure_fraction=0.0,
            reasons=(0,),  # type: ignore[arg-type]
            event_time=EVENT_TIME,
            safety_id="safety-1",
        )


@pytest.mark.parametrize("value", [1, 0, "true", None, object()])
def test_rejects_invalid_approved_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="approved must be a bool"):
        PreTradeSafetyOutput(
            approved=value,  # type: ignore[arg-type]
            action="NO_TRADE",
            exposure_fraction=0.0,
            reasons=("RISK_REJECTED",),
            event_time=EVENT_TIME,
            safety_id="safety-1",
        )


@pytest.mark.parametrize("value", ["", "   "])
def test_rejects_blank_contract_version(value: str) -> None:
    with pytest.raises(ValueError, match="contract_version must not be empty"):
        PreTradeSafetyOutput(
            approved=False,
            action="NO_TRADE",
            exposure_fraction=0.0,
            reasons=("RISK_REJECTED",),
            event_time=EVENT_TIME,
            safety_id="safety-1",
            contract_version=value,
        )


@pytest.mark.parametrize("value", [0, None, object()])
def test_rejects_invalid_contract_version_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="contract_version must be a string"):
        PreTradeSafetyOutput(
            approved=False,
            action="NO_TRADE",
            exposure_fraction=0.0,
            reasons=("RISK_REJECTED",),
            event_time=EVENT_TIME,
            safety_id="safety-1",
            contract_version=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("value", ["2.0.0", " 1.0.0 ", "unknown"])
def test_rejects_unsupported_contract_versions(value: str) -> None:
    with pytest.raises(ValueError, match="unsupported contract_version"):
        PreTradeSafetyOutput(
            approved=False,
            action="NO_TRADE",
            exposure_fraction=0.0,
            reasons=("RISK_REJECTED",),
            event_time=EVENT_TIME,
            safety_id="safety-1",
            contract_version=value,
        )


@pytest.mark.parametrize("value", ["", "   ", "\t"])
def test_rejects_blank_reason_values(value: str) -> None:
    with pytest.raises(ValueError, match="reasons must not contain blank values"):
        PreTradeSafetyOutput(
            approved=False,
            action="NO_TRADE",
            exposure_fraction=0.0,
            reasons=(value,),
            event_time=EVENT_TIME,
            safety_id="safety-1",
        )
