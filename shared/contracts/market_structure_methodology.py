"""FILE: shared/contracts/market_structure_methodology.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.1
DATE_GREGORIAN: 2026-09-30
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the project-owned deterministic baseline methodology for descriptive market structure.
LAYER: shared
OWNS: deterministic structure rules and methodology configuration semantics.
DOES_NOT_OWN: provider I/O, persistence, trading decisions, risk, execution.
DEPENDENCIES: stdlib:dataclasses
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass

MARKET_STRUCTURE_METHODOLOGY_ID = "deterministic_confirmed_pivot_structure"
MARKET_STRUCTURE_METHODOLOGY_VERSION = "1.0.0"
MARKET_STRUCTURE_METHODOLOGY_CONTRACT_ID = "market_structure_methodology"
MARKET_STRUCTURE_METHODOLOGY_CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class MarketStructureMethodology:
    """Versioned deterministic baseline; no trading action semantics."""

    pivot_left_bars: int = 2
    pivot_right_bars: int = 2
    state_lookback: int = 10
    expansion_ratio: float = 1.25
    compression_ratio: float = 0.75

    def __post_init__(self) -> None:
        for name, value in (
            ("pivot_left_bars", self.pivot_left_bars),
            ("pivot_right_bars", self.pivot_right_bars),
            ("state_lookback", self.state_lookback),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be an integer >= 1")

        if self.state_lookback < 2:
            raise ValueError("state_lookback must be >= 2")

        if not 1.0 < self.expansion_ratio:
            raise ValueError("expansion_ratio must be > 1")

        if not 0.0 < self.compression_ratio < 1.0:
            raise ValueError("compression_ratio must be between 0 and 1")


METHODOLOGY = MarketStructureMethodology()


def methodology_rules() -> tuple[str, ...]:
    """Return the normative deterministic rules used by the baseline."""

    return (
        "A swing high is a bar high strictly greater than every high in the configured left and right confirmation windows.",
        "A swing low is a bar low strictly lower than every low in the configured left and right confirmation windows.",
        "A confirmed high is HH when above the previous confirmed high; otherwise LH.",
        "A confirmed low is HL when above the previous confirmed low; otherwise LL.",
        "A breakout occurs when the point-in-time close is strictly above the latest confirmed swing-high level.",
        "A breakdown occurs when the point-in-time close is strictly below the latest confirmed swing-low level.",
        "A structure shift occurs when a breakout follows a bearish structural sequence or a breakdown follows a bullish structural sequence.",
        "State width is the high-low envelope of the current state window compared with the immediately preceding equal-length window.",
        "Expansion is current width / prior width >= expansion_ratio; compression is <= compression_ratio; otherwise state is range.",
        "A pivot is not considered confirmed until its full right confirmation window has elapsed.",
        "Insufficient history fails deterministically; future observations never participate in a point-in-time result.",
        "The methodology is descriptive only and emits no BUY, SELL, order, position, sizing, risk, or execution instruction.",
        "The same rules and configuration apply to Crypto, Forex, and Gold; provider-specific adaptations require a separate versioned methodology.",
    )
