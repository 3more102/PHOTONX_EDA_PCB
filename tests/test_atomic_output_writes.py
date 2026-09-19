import json
from pathlib import Path

import pytest

import photonx_eda_pcb.io.safe_write as safe_write
from photonx_eda_pcb.exporters import export_json
from photonx_eda_pcb.io.project_store import write_reconstruction_bundle
from photonx_eda_pcb.io.safe_write import atomic_write_text
from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.validation import ValidationReport


def test_atomic_write_failure_preserves_existing_target_and_cleans_temp(tmp_path, monkeypatch):
    target = tmp_path / "artifact.txt"
    target.write_text("old", encoding="utf-8")

    def fail_replace(source, destination):
        raise OSError("replace failed")

    monkeypatch.setattr(safe_write.os, "replace", fail_replace)

    with pytest.raises(OSError, match="replace failed"):
        atomic_write_text(target, "new")

    assert target.read_text(encoding="utf-8") == "old"
    assert list(tmp_path.glob("artifact.txt.*")) == []


def test_json_export_uses_atomic_replace(tmp_path, monkeypatch):
    target = tmp_path / "board.json"
    target.write_text('{"stale": true}', encoding="utf-8")
    calls = []
    real_replace = safe_write.os.replace

    def recording_replace(source, destination):
        calls.append((Path(source), Path(destination)))
        return real_replace(source, destination)

    monkeypatch.setattr(safe_write.os, "replace", recording_replace)

    result = export_json(BoardModel(), target)

    assert result == target
    assert calls and calls[-1][1] == target
    assert json.loads(target.read_text(encoding="utf-8"))["tracks"] == []


def test_reconstruction_bundle_uses_atomic_replace_for_both_json_files(tmp_path, monkeypatch):
    calls = []
    real_replace = safe_write.os.replace

    def recording_replace(source, destination):
        calls.append((Path(source), Path(destination)))
        return real_replace(source, destination)

    monkeypatch.setattr(safe_write.os, "replace", recording_replace)

    root = write_reconstruction_bundle(BoardModel(), ValidationReport(), tmp_path / "bundle")

    assert root == tmp_path / "bundle"
    assert [destination.name for _, destination in calls] == ["board.json", "validation.json"]
    assert json.loads((root / "board.json").read_text(encoding="utf-8"))["tracks"] == []
    assert json.loads((root / "validation.json").read_text(encoding="utf-8"))["ok"] is True
