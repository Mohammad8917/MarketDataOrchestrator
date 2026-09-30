from dataclasses import dataclass
from datetime import datetime, timezone
import math

CONTRACT_ID = "regime_uncertainty_boundary"
CONTRACT_VERSION = "1.0.0"

@dataclass(frozen=True, slots=True)
class RegimeUncertaintyRequest:
    confidence: float
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        if not self.source_event_id:
            raise ValueError("source_event_id must be non-empty")
        for value in (self.event_time, self.received_at):
            if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
                raise ValueError("timestamps must be timezone-aware UTC")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not math.isfinite(float(self.confidence)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be finite and within [0, 1]")

@dataclass(frozen=True, slots=True)
class RegimeUncertaintyOutput:
    uncertainty_score: float
    event_time: datetime
    source_event_id: str
