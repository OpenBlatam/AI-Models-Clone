import builtins
import io
import pytest

from agents.backend.onyx.server.features.heygen_ai.security_config import SecurityConfigManager


def test_save_configuration_failure(monkeypatch, tmp_path):
    mgr = SecurityConfigManager(str(tmp_path / "cfg.json"))

    def fake_open(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(builtins, "open", fake_open)
    ok = mgr.save_configuration()
    assert ok is False











