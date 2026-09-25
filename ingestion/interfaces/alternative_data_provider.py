"""FILE: ingestion/interfaces/alternative_data_provider.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the canonical asynchronous alternative-data provider boundary.
LAYER: ingestion
OWNS: Alternative-data event contract and asynchronous provider interface.
DOES_NOT_OWN: Concrete transport, credentials, persistence, analysis, strategy, decision, risk.
DEPENDENCIES: stdlib:dataclasses; stdlib:datetime; stdlib:typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class AlternativeDataEvent:
    source_event_id: str
    source: str
    event_time: datetime
    received_at: datetime
    payload_digest: str


@runtime_checkable
class AlternativeDataProvider(Protocol):
    provider_id: str

    async def fetch(
        self, query: str, *, start: datetime, end: datetime
    ) -> tuple[AlternativeDataEvent, ...]: ...
