from types import SimpleNamespace

import pytest

from photonx_eda_pcb.exporters import validate_with_kicad_cli
from photonx_eda_pcb.exporters import kicad


def test_kicad_cli_validation_passes_bounded_timeout(monkeypatch, tmp_path):
    seen = {}

    monkeypatch.setattr(kicad.shutil, "which", lambda _name: "/fake/kicad-cli")

    def fake_run(args, **kwargs):
        seen["args"] = args
        seen["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout="clean", stderr="")

    monkeypatch.setattr(kicad.subprocess, "run", fake_run)

    ok, detail = validate_with_kicad_cli(tmp_path / "board.kicad_pcb", timeout_s=12.5)

    assert ok is True
    assert detail == "clean"
    assert seen["args"][-1] == "--exit-code-violations"
    assert seen["kwargs"]["timeout"] == 12.5
    assert seen["kwargs"]["capture_output"] is True
    assert seen["kwargs"]["text"] is True


def test_kicad_cli_validation_timeout_is_indeterminate(monkeypatch, tmp_path):
    monkeypatch.setattr(kicad.shutil, "which", lambda _name: "/fake/kicad-cli")

    def fake_run(*_args, **_kwargs):
        raise kicad.subprocess.TimeoutExpired(cmd="kicad-cli", timeout=0.25)

    monkeypatch.setattr(kicad.subprocess, "run", fake_run)

    ok, detail = validate_with_kicad_cli(tmp_path / "board.kicad_pcb", timeout_s=0.25)

    assert ok is None
    assert detail == "kicad-cli validation timed out after 0.25s"


def test_kicad_cli_validation_launch_failure_is_indeterminate(monkeypatch, tmp_path):
    monkeypatch.setattr(kicad.shutil, "which", lambda _name: "/fake/kicad-cli")

    def fake_run(*_args, **_kwargs):
        raise OSError("permission denied")

    monkeypatch.setattr(kicad.subprocess, "run", fake_run)

    ok, detail = validate_with_kicad_cli(tmp_path / "board.kicad_pcb")

    assert ok is None
    assert detail == "kicad-cli failed to start: permission denied"


@pytest.mark.parametrize("timeout_s", [0, -1, float("inf"), float("nan"), "bad"])
def test_kicad_cli_validation_rejects_invalid_timeout(monkeypatch, tmp_path, timeout_s):
    monkeypatch.setattr(kicad.shutil, "which", lambda _name: "/fake/kicad-cli")
    with pytest.raises(ValueError, match="positive finite"):
        validate_with_kicad_cli(tmp_path / "board.kicad_pcb", timeout_s=timeout_s)
