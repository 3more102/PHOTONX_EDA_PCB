import json
from types import SimpleNamespace as NS

from photonx_eda_pcb import cli
from photonx_eda_pcb.exporters.kicad_report import KicadExportReport


def test_reconstruct_kicad_writes_connectivity_roundtrip_artifact(
    tmp_path,
    monkeypatch,
):
    source = tmp_path / "input"
    source.mkdir()
    output = tmp_path / "out"

    board = object()
    validation = NS(ok=True)
    preflight = {
        "discovered_files": ["board.gbr"],
        "ready_for_strict_reconstruction": True,
    }
    report = KicadExportReport()
    roundtrip = {
        "scope": [
            "net_table",
            "tracks",
            "recovered_pads",
            "copper_regions",
            "recovered_slots",
        ],
        "roundtrip_equal": True,
        "source_connectivity_complete": True,
        "source_equivalent": True,
        "nets": {"equal": True},
        "tracks": {"equal": True},
        "pads": {"equal": True},
        "regions": {"equal": True},
        "slots": {"equal": True},
        "losses": {
            "skipped_track_ids": [],
            "skipped_region_ids": [],
            "skipped_slot_ids": [],
            "unresolved_pad_net_ids": [],
            "unresolved_slot_net_ids": [],
        },
        "issues": [],
    }

    monkeypatch.setattr(
        cli,
        "inspect_input",
        lambda _path: NS(to_dict=lambda: preflight),
    )
    monkeypatch.setattr(
        cli,
        "reconstruct",
        lambda *_args, **_kwargs: NS(board=board, validation=validation),
    )
    monkeypatch.setattr(cli, "write_reconstruction_bundle", lambda *_args: None)
    monkeypatch.setattr(cli, "export_json", lambda *_args: None)
    monkeypatch.setattr(cli, "summary", lambda *_args: {"ok": True})

    def fake_export(_board, path):
        path.write_text("(kicad_pcb)\n", encoding="utf-8")
        return path, report

    monkeypatch.setattr(cli, "export_kicad_with_report", fake_export)
    monkeypatch.setattr(
        cli,
        "write_omission_manifest",
        lambda _report, path: path.write_text("{}\n", encoding="utf-8"),
    )
    monkeypatch.setattr(
        cli,
        "validate_kicad_connectivity_roundtrip",
        lambda *_args: roundtrip,
    )
    monkeypatch.setattr(
        cli,
        "validate_with_kicad_cli",
        lambda _path: (None, "kicad-cli not found"),
    )

    assert cli.main(
        [
            "reconstruct",
            str(source),
            "--output",
            str(output),
            "--kicad",
        ]
    ) == 0

    payload = json.loads(
        (output / "kicad_connectivity_roundtrip.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload == roundtrip
