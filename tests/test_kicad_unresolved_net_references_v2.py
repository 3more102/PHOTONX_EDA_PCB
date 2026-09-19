from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.models import BoardModel, NetGroup, PadCandidate, Point, Track


def _pad_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.lstrip().startswith("(pad ")]


def test_unknown_pad_net_preserves_geometry_without_net_claim(tmp_path):
    board = BoardModel(
        pads=[
            PadCandidate(
                "P1",
                Point(1.0, 2.0),
                1.0,
                1.0,
                "R",
                "F.Cu",
                net_id="MISSING",
            )
        ]
    )

    path, report = export_kicad_with_report(board, tmp_path / "unknown-pad-net.kicad_pcb")
    lines = _pad_lines(path.read_text(encoding="utf-8"))

    assert len(lines) == 1
    assert "(net " not in lines[0]
    assert any(
        issue.code == "KICAD_NET_REFERENCE_UNRESOLVED"
        and issue.object_id == "P1"
        for issue in report.issues
    )


def test_unknown_track_net_is_omitted_not_relabelled_net_zero(tmp_path):
    board = BoardModel(
        tracks=[
            Track(
                "T1",
                Point(0.0, 0.0),
                Point(1.0, 0.0),
                0.2,
                "F.Cu",
                net_id="MISSING",
            )
        ]
    )

    path, report = export_kicad_with_report(board, tmp_path / "unknown-track-net.kicad_pcb")
    text = path.read_text(encoding="utf-8")

    assert "(segment " not in text
    assert report.exported_tracks == 0
    assert report.skipped_tracks == 1
    assert report.skipped_track_ids == ["T1"]
    assert any(
        issue.code == "KICAD_NET_REFERENCE_UNRESOLVED"
        and issue.object_id == "T1"
        for issue in report.issues
    )


def test_unassigned_track_still_exports_as_explicit_net_zero(tmp_path):
    board = BoardModel(
        tracks=[
            Track(
                "T1",
                Point(0.0, 0.0),
                Point(1.0, 0.0),
                0.2,
                "F.Cu",
            )
        ]
    )

    path, report = export_kicad_with_report(board, tmp_path / "unassigned-track.kicad_pcb")
    text = path.read_text(encoding="utf-8")

    assert "(segment " in text
    assert "(net 0)" in text
    assert report.exported_tracks == 1
    assert report.skipped_tracks == 0
    assert not any(
        issue.code == "KICAD_NET_REFERENCE_UNRESOLVED"
        for issue in report.issues
    )


def test_known_net_assignments_remain_unchanged(tmp_path):
    board = BoardModel(
        tracks=[
            Track(
                "T1",
                Point(0.0, 0.0),
                Point(1.0, 0.0),
                0.2,
                "F.Cu",
                net_id="N1",
            )
        ],
        pads=[
            PadCandidate(
                "P1",
                Point(1.0, 0.0),
                1.0,
                1.0,
                "R",
                "F.Cu",
                net_id="N1",
            )
        ],
        nets=[NetGroup("N1", ["T1", "P1"], 1.0, label="GND")],
    )

    path, report = export_kicad_with_report(board, tmp_path / "known-net.kicad_pcb")
    text = path.read_text(encoding="utf-8")

    assert '(net 1 "GND")' in text
    assert "(segment " in text and "(net 1)" in text
    assert any('(net 1 "GND")' in line for line in _pad_lines(text))
    assert report.exported_tracks == 1
    assert report.skipped_tracks == 0
    assert not any(
        issue.code == "KICAD_NET_REFERENCE_UNRESOLVED"
        for issue in report.issues
    )


def test_plated_slot_with_unknown_but_consistent_net_keeps_geometry_without_net_claim(tmp_path):
    slot = SlotFeature("S", (0, 0), (4, 0), 1, "plated")
    board = BoardModel(
        pads=[
            PadCandidate("F", Point(2, 0), 6, 2, "O", "F.Cu", net_id="MISSING"),
            PadCandidate("B", Point(2, 0), 6, 2, "O", "B.Cu", net_id="MISSING"),
        ],
        slots=[slot],
    )

    path, report = export_kicad_with_report(board, tmp_path / "slot-unknown-net.kicad_pcb")
    text = path.read_text(encoding="utf-8")
    slot_pad = next(
        line for line in _pad_lines(text)
        if "thru_hole" in line
    )

    assert "RecoveredPlatedSlot" in text
    assert "(net " not in slot_pad
    assert "S" in report.exported_slot_ids
    assert any(
        issue.code == "KICAD_NET_REFERENCE_UNRESOLVED"
        and issue.object_id == "S"
        for issue in report.issues
    )
