from __future__ import annotations

from sediment_palace.config import load_config


def test_load_config_from_env(monkeypatch):
    monkeypatch.setenv("SEDIMENT_PROJECT_ROOT", ".")
    monkeypatch.setenv("SEDIMENT_TIMEOUT_DEFAULT_SECONDS", "3.5")
    monkeypatch.setenv("SEDIMENT_TIMEOUT_METABOLIZE_SECONDS", "9.0")
    monkeypatch.setenv("SEDIMENT_BUDGET_WRITE_CONTENT", "123")
    cfg = load_config()
    assert cfg.timeout_default_seconds == 3.5
    assert cfg.timeout_metabolize_seconds == 9.0
    assert cfg.write_content_budget == 123
