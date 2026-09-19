import json
from pathlib import Path

from photonx_eda_pcb import board_fingerprint, reconstruct
from photonx_eda_pcb.cli import main
from photonx_eda_pcb.io import write_reconstruction_bundle


FIX = Path(__file__).parent / "fixtures" / "led"


def test_fingerprint_cli_emits_deterministic_manifest(capsys):
    rc = main(["fingerprint", str(FIX)])
    payload = json.loads(capsys.readouterr().out)

    assert rc == 0
    assert payload["schema_version"] == 1
    assert payload["algorithm"] == "sha256"
    assert payload["scope"] == "canonical-roundtrip-board"
    assert len(payload["sha256"]) == 64
    assert payload["summary"]["validation_ok"] is True

    rc = main(["fingerprint", str(FIX)])
    repeated = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert repeated["sha256"] == payload["sha256"]


def test_fingerprint_cli_can_write_json(tmp_path, capsys):
    output = tmp_path / "fingerprint.json"
    rc = main(["fingerprint", str(FIX), "--output", str(output)])
    printed = json.loads(capsys.readouterr().out)

    assert rc == 0
    assert json.loads(output.read_text(encoding="utf-8")) == printed


def test_reconstruction_bundle_contains_fingerprint(tmp_path):
    result = reconstruct(FIX)
    root = write_reconstruction_bundle(result.board, result.validation, tmp_path)
    payload = json.loads((root / "fingerprint.json").read_text(encoding="utf-8"))

    assert payload["sha256"] == board_fingerprint(result.board)
    assert payload["summary"]["validation_ok"] is True
