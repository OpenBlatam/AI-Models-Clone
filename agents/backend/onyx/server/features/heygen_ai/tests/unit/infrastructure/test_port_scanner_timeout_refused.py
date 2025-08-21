import asyncio
import pytest

from agents.backend.onyx.server.features.heygen_ai.port_scanner import AsyncPortScanner


@pytest.mark.asyncio
async def test_scan_single_port_timeout(monkeypatch):
    async def fake_open_connection(host, port):
        await asyncio.sleep(0)  # yield control
        raise asyncio.TimeoutError

    import agents.backend.onyx.server.features.heygen_ai.port_scanner as mod
    monkeypatch.setattr(mod.asyncio, "open_connection", fake_open_connection)

    scanner = AsyncPortScanner(timeout_seconds=0.01)
    res = await scanner.scan_single_port("localhost", 1)
    assert res.is_port_open is False
    assert res.error_message == "Connection timeout"


@pytest.mark.asyncio
async def test_scan_single_port_refused(monkeypatch):
    async def fake_open_connection(host, port):
        await asyncio.sleep(0)
        raise ConnectionRefusedError

    import agents.backend.onyx.server.features.heygen_ai.port_scanner as mod
    monkeypatch.setattr(mod.asyncio, "open_connection", fake_open_connection)

    scanner = AsyncPortScanner(timeout_seconds=0.01)
    res = await scanner.scan_single_port("localhost", 2)
    assert res.is_port_open is False
    assert res.error_message == "Connection refused"












