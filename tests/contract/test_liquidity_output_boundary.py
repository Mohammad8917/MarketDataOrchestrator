"""Adversarial contract tests for liquidity output boundaries."""

from datetime import datetime, timezone

import pytest

from shared.contracts.liquidity import LiquidityOutput


@pytest.mark.parametrize("value", [0, 1, 0.0, 1.0, "true", None])
def test_liquidity_output_rejects_non_boolean_approved(value: object) -> None:
    with pytest.raises(ValueError, match="approved must be a boolean"):
        LiquidityOutput(
            approved=value,  # type: ignore[arg-type]
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            liquidity_id="liquidity-1",
        )


@pytest.mark.parametrize("version", ["", "   ", "\\t", "\\n"])
def test_liquidity_output_rejects_blank_contract_version(version: str) -> None:
    with pytest.raises(ValueError, match="contract_version must not be empty"):
        LiquidityOutput(
            approved=True,
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            liquidity_id="liquidity-1",
            contract_version=version,
        )
