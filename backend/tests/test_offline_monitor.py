
import asyncio

import pytest

from backend.app import main


def test_offline_monitor_marks_stale_devices(monkeypatch):
    calls = []

    def fake_mark_offline_devices():
        calls.append(True)
        return 2

    async def stop_after_first_cycle(delay):
        raise asyncio.CancelledError

    monkeypatch.setattr(
        main,
        "mark_offline_devices",
        fake_mark_offline_devices,
    )

    monkeypatch.setattr(
        main.asyncio,
        "sleep",
        stop_after_first_cycle,
    )

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(main.offline_device_monitor())

    assert len(calls) == 1


def test_offline_monitor_continues_after_database_error(monkeypatch):
    calls = []

    def fake_mark_offline_devices():
        calls.append(True)

        if len(calls) == 1:
            raise RuntimeError("Database temporarily unavailable")

        return 0

    async def stop_after_second_cycle(delay):
        if len(calls) >= 2:
            raise asyncio.CancelledError

    monkeypatch.setattr(
        main,
        "mark_offline_devices",
        fake_mark_offline_devices,
    )

    monkeypatch.setattr(
        main.asyncio,
        "sleep",
        stop_after_second_cycle,
    )

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(main.offline_device_monitor())

    assert len(calls) == 2


def test_offline_monitor_can_be_cancelled():
    async def run_test():
        task = asyncio.create_task(
            main.offline_device_monitor()
        )

        await asyncio.sleep(0)

        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run_test())

