"""FILE: tests/integration/test_ingestion_service.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.1
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify asynchronous ingestion isolation, timeout enforcement, deterministic ordering, and bounded concurrency.
LAYER: tests
OWNS: Integration verification for ingestion orchestration.
DOES_NOT_OWN: Production ingestion policy or provider transport.
DEPENDENCIES: stdlib:asyncio; stdlib:datetime; pytest; ingestion.ingestion_service; ingestion.interfaces.market_provider
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from ingestion.ingestion_service import IngestionService
from ingestion.interfaces.market_provider import MarketDataProvider, MarketEvent


class FakeProvider:
    def __init__(
        self,
        provider_id: str,
        events: tuple[MarketEvent, ...] = (),
        error: Exception | None = None,
        delay: float = 0.0,
        active: dict[str, int] | None = None,
    ) -> None:
        self.provider_id = provider_id
        self.events = events
        self.error = error
        self.delay = delay
        self.active = active

    async def fetch(
        self, symbol: str, *, start: datetime, end: datetime
    ) -> tuple[MarketEvent, ...]:
        if self.active is not None:
            self.active["current"] += 1
            self.active["peak"] = max(self.active["peak"], self.active["current"])
        try:
            if self.delay:
                await asyncio.sleep(self.delay)
            if self.error is not None:
                raise self.error
            return self.events
        finally:
            if self.active is not None:
                self.active["current"] -= 1


def event(source: str, offset: int) -> MarketEvent:
    now = datetime(2026, 9, 24, 9, tzinfo=timezone.utc)
    return MarketEvent(
        f"{source}-{offset}",
        source,
        "BTCUSDT",
        now + timedelta(seconds=offset),
        now,
        f"sha256:{source}-{offset}",
    )


def request_window() -> tuple[datetime, datetime]:
    return (
        datetime(2026, 9, 24, 9, tzinfo=timezone.utc),
        datetime(2026, 9, 24, 10, tzinfo=timezone.utc),
    )


@pytest.mark.asyncio
async def test_collect_isolates_provider_failure_and_orders_events() -> None:
    start, end = request_window()
    providers = (
        FakeProvider("good", (event("good", 2), event("good", 1))),
        FakeProvider("bad", error=RuntimeError("provider unavailable")),
    )
    result = await IngestionService(providers).collect("BTCUSDT", start=start, end=end)
    assert [item.source_event_id for item in result] == ["good-1", "good-2"]


@pytest.mark.asyncio
async def test_collect_timeout_isolated_from_healthy_provider() -> None:
    start, end = request_window()
    providers = (
        FakeProvider("slow", (event("slow", 1),), delay=0.05),
        FakeProvider("fast", (event("fast", 2),)),
    )
    result = await IngestionService(providers, timeout_seconds=0.01).collect(
        "BTCUSDT", start=start, end=end
    )
    assert [item.source_event_id for item in result] == ["fast-2"]


@pytest.mark.asyncio
async def test_collect_enforces_real_bounded_concurrency_across_400_providers() -> None:
    start, end = request_window()
    active = {"current": 0, "peak": 0}
    providers = tuple(
        FakeProvider(
            f"provider-{index:03d}",
            (event(f"provider-{index:03d}", index),),
            delay=0.001,
            active=active,
        )
        for index in range(400)
    )
    result = await IngestionService(providers, concurrency=4, timeout_seconds=2).collect(
        "BTCUSDT", start=start, end=end
    )
    assert active["peak"] <= 4
    assert len(result) == 400
    assert len({item.source_event_id for item in result}) == 400
    assert [item.source_event_id for item in result] == sorted(
        (item.source_event_id for item in result), key=lambda value: (int(value.split("-")[-1]),)
    )


@pytest.mark.asyncio
async def test_collect_is_deterministic_when_completion_order_changes() -> None:
    start, end = request_window()

    async def run(delays: tuple[float, ...]) -> tuple[str, ...]:
        providers = tuple(
            FakeProvider(f"p-{index}", (event(f"p-{index}", index),), delay=delay)
            for index, delay in enumerate(delays)
        )
        result = await IngestionService(providers, concurrency=4).collect(
            "BTCUSDT", start=start, end=end
        )
        return tuple(item.source_event_id for item in result)

    first = await run((0.04, 0.001, 0.03, 0.002))
    second = await run((0.002, 0.03, 0.001, 0.04))
    assert first == second == ("p-0-0", "p-1-1", "p-2-2", "p-3-3")


@pytest.mark.asyncio
async def test_collect_preserves_duplicate_identity_without_implicit_deduplication() -> None:
    start, end = request_window()
    duplicate = event("same", 1)
    providers = (FakeProvider("a", (duplicate,)), FakeProvider("b", (duplicate,)))
    result = await IngestionService(providers).collect("BTCUSDT", start=start, end=end)
    assert result == (duplicate, duplicate)


@pytest.mark.asyncio
async def test_collect_propagates_cancellation() -> None:
    start, end = request_window()
    task = asyncio.create_task(
        IngestionService((FakeProvider("slow", delay=1.0),)).collect(
            "BTCUSDT", start=start, end=end
        )
    )
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_collect_empty_provider_set() -> None:
    start, end = request_window()
    result = await IngestionService(()).collect("BTCUSDT", start=start, end=end)
    assert result == ()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("start", "end"),
    [
        (datetime(2026, 9, 24, 9), datetime(2026, 9, 24, 10, tzinfo=timezone.utc)),
        (
            datetime(2026, 9, 24, 9, tzinfo=timezone.utc),
            datetime(2026, 9, 24, 10),
        ),
        (
            datetime(2026, 9, 24, 10, tzinfo=timezone.utc),
            datetime(2026, 9, 24, 9, tzinfo=timezone.utc),
        ),
    ],
)
async def test_collect_rejects_invalid_temporal_window(start: datetime, end: datetime) -> None:
    with pytest.raises(ValueError):
        await IngestionService(()).collect("BTCUSDT", start=start, end=end)


@pytest.mark.asyncio
async def test_collect_rejects_blank_symbol() -> None:
    start, end = request_window()
    with pytest.raises(ValueError, match="symbol"):
        await IngestionService(()).collect("   ", start=start, end=end)


def test_market_event_rejects_non_utc_event_time() -> None:
    now = datetime(2026, 9, 24, 9)
    with pytest.raises(ValueError, match="event_time"):
        MarketEvent("evt", "provider", "BTCUSDT", now, now.replace(tzinfo=timezone.utc), "sha256:x")


def test_market_event_rejects_non_utc_received_at() -> None:
    now = datetime(2026, 9, 24, 9, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="received_at"):
        MarketEvent("evt", "provider", "BTCUSDT", now, now.replace(tzinfo=None), "sha256:x")


def test_provider_protocol_is_runtime_checkable() -> None:
    provider = FakeProvider("provider")
    assert isinstance(provider, MarketDataProvider)


def test_concurrency_and_timeout_must_be_positive() -> None:
    with pytest.raises(ValueError, match="positive"):
        IngestionService((), concurrency=0)
    with pytest.raises(ValueError, match="positive"):
        IngestionService((), timeout_seconds=0)
