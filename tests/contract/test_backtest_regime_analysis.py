from backtest.regime_analyzer import (
    CONTRACT_ID,
    CONTRACT_VERSION,
    RegimeAnalysisReplay,
    RegimeAnalysisReplayOutput,
)


def test_contract_identity() -> None:
    replay = RegimeAnalysisReplay(
        trend_lookback=4,
        volatility_short_lookback=2,
        volatility_long_lookback=4,
    )
    assert replay.contract_id == CONTRACT_ID
    assert replay.contract_version == CONTRACT_VERSION
    assert CONTRACT_ID == "backtest_regime_analysis_boundary"
    assert CONTRACT_VERSION == "1.0.0"


def test_output_is_frozen_and_empty_output_is_valid() -> None:
    output = RegimeAnalysisReplayOutput(())
    assert output.results == ()
    assert output.contract_version == "1.0.0"
    assert output.__dataclass_params__.frozen is True
