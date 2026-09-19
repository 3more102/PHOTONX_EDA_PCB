import json
from types import SimpleNamespace as NS

from photonx_eda_pcb import cli
from photonx_eda_pcb.exporters.kicad_report import KicadExportIssue, KicadExportReport


def _report():
    return KicadExportReport(
        exported_slots=1,
        skipped_slots=1,
        exported_regions=1,
        skipped_regions=1,
        exported_tracks=1,
        skipped_tracks=1,
        skipped_routes=1,
        issues=[
            KicadExportIssue(
                "warning",
                "KICAD_SLOT_PLATING_UNKNOWN",
                "S_SKIP",
                "slot plating is unknown",
            ),
            KicadExportIssue(
                "warning",
                "KICAD_COPPER_REGION_INVALID_GEOMETRY",
                "R_SKIP",
                "invalid region topology",
            ),
            KicadExportIssue(
                "warning",
                "KICAD_NET_REFERENCE_UNRESOLVED",
                "T_SKIP",
                "unknown track net",
            ),
            KicadExportIssue(
                "warning",
                "KICAD_ARBITRARY_ROUTE_UNSUPPORTED",
                "Q_SKIP",
                "route omitted",
            ),
        ],
        exported_slot_ids=["S_OK"],
        skipped_slot_ids=["S_SKIP"],
        exported_region_ids=["R_OK"],
        skipped_region_ids=["R_SKIP"],
        exported_track_ids=["T_OK"],
        skipped_track_ids=["T_SKIP"],
        skipped_route_ids=["Q_SKIP"],
    )


def test_write_kicad_export_report_preserves_current_report_surface(tmp_path):
    report = _report()

    path = cli._write_kicad_export_report(
        tmp_path / "kicad_export_report.json",
        report,
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["ok"] is True
    assert payload["exported_regions"] == 1
    assert payload["skipped_regions"] == 1
    assert payload["exported_tracks"] == 1
    assert payload["skipped_tracks"] == 1
    assert payload["skipped_routes"] == 1
    assert payload["exported_region_ids"] == ["R_OK"]
    assert payload["skipped_region_ids"] == ["R_SKIP"]
    assert payload["exported_track_ids"] == ["T_OK"]
    assert payload["skipped_track_ids"] == ["T_SKIP"]
    assert payload["skipped_route_ids"] == ["Q_SKIP"]
    assert payload["issues"][0]["code"] == "KICAD_SLOT_PLATING_UNKNOWN"


def test_write_kicad_export_report_marks_errors_not_ok(tmp_path):
    report = KicadExportReport(
        issues=[
            KicadExportIssue(
                "error",
                "KICAD_EXPORT_ERROR",
                "X",
                "failed",
            )
        ]
    )

    path = cli._write_kicad_export_report(tmp_path / "report.json", report)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["ok"] is False


def test_reconstruct_kicad_emits_board_report_omissions_and_validation(
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
    report = _report()

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
    roundtrip = {
        "scope": [\n            "net_table",\n            "tracks",\n            "recovered_pads",\n            "copper_regions",\n            "recovered_slots",\n        ],
        "roundtrip_equal": True,
        "source_connectivity_complete": False,
        "source_equivalent": False,
        "nets": {"equal": True},
        "tracks": {"equal": True},
        "pads": {"equal": True},
        "losses": {"skipped_track_ids": ["T_SKIP"], "unresolved_pad_net_ids": []},
        "issues": [],
    }
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

    assert (output / "reconstructed.kicad_pcb").read_text(encoding="utf-8") == "(kicad_pcb)\n"

    audit = json.loads(
        (output / "kicad_export_report.json").read_text(encoding="utf-8")
    )
    assert audit["ok"] is True
    assert audit["skipped_tracks"] == 1
    assert audit["skipped_routes"] == 1

    omissions = json.loads(
        (output / "kicad_omissions.json").read_text(encoding="utf-8")
    )
    assert omissions["exported_slots"] == ["S_OK"]
    assert omissions["skipped_slots"] == ["S_SKIP"]
    assert omissions["exported_regions"] == ["R_OK"]
    assert omissions["skipped_regions"] == ["R_SKIP"]
    assert omissions["exported_tracks"] == ["T_OK"]
    assert omissions["skipped_tracks"] == ["T_SKIP"]
    assert omissions["omitted_routes"] == ["Q_SKIP"]

    connectivity = json.loads(
        (output / "kicad_connectivity_roundtrip.json").read_text(encoding="utf-8")
    )
    assert connectivity["roundtrip_equal"] is True
    assert connectivity["source_connectivity_complete"] is False
    assert connectivity["losses"]["skipped_track_ids"] == ["T_SKIP"]

    assert (output / "kicad_validation.txt").read_text(
        encoding="utf-8"
    ) == "status=None\nkicad-cli not found\n"
