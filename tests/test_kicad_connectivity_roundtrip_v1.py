from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.models import BoardModel, NetGroup, PadCandidate, Point, Track
from photonx_eda_pcb.roundtrip import validate_kicad_connectivity_roundtrip


def _net(net_id="N1", label="GND"):
    return NetGroup(net_id, [], 1.0, label)


def test_kicad_connectivity_roundtrip_matches_export_policy_and_reports_losses(tmp_path):
    board = BoardModel(
        nets=[_net()],
        tracks=[
            Track("T1", Point(0, 0), Point(2, 0), 0.25, "F.Cu", "N1"),
            Track("T0", Point(0, 1), Point(2, 1), 0.25, "F.Cu", None),
            Track("T_SKIP", Point(0, 2), Point(2, 2), 0.25, "F.Cu", "MISSING"),
        ],
        pads=[
            PadCandidate("P1", Point(1, 0), 1.2, 1.2, "C", "F.Cu", None, "N1"),
            PadCandidate(
                "P_UNRESOLVED",
                Point(1, 2),
                1.0,
                1.0,
                "R",
                "F.Cu",
                None,
                "MISSING",
            ),
        ],
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    audit = validate_kicad_connectivity_roundtrip(board, path, report)

    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
    assert audit["losses"] == {
        "ambiguous_net_ids": [],
        "skipped_drill_ids": [],
        "skipped_outline_ids": [],
        "skipped_pad_ids": [],
        "skipped_track_ids": ["T_SKIP"],
        "skipped_region_ids": [],
        "skipped_slot_ids": [],
        "unresolved_pad_net_ids": ["P_UNRESOLVED"],
        "unresolved_slot_net_ids": [],
        "omitted_route_ids": [],
        "omitted_proven_via_span_drill_ids": [],
    }
    assert audit["tracks"]["expected_count"] == 2
    assert audit["tracks"]["observed_count"] == 2
    assert audit["pads"]["equal"] is True
    assert audit["nets"]["equal"] is True


def test_kicad_connectivity_roundtrip_is_source_equivalent_when_nothing_is_lost(tmp_path):
    board = BoardModel(
        nets=[_net()],
        tracks=[Track("T1", Point(0, 0), Point(2, 0), 0.25, "F.Cu", "N1")],
        pads=[PadCandidate("P1", Point(1, 0), 1.0, 1.0, "C", "F.Cu", None, "N1")],
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    audit = validate_kicad_connectivity_roundtrip(board, path, report)

    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is True
    assert audit["source_equivalent"] is True
    assert audit["issues"] == []


def test_kicad_connectivity_roundtrip_detects_changed_track_net(tmp_path):
    board = BoardModel(
        nets=[_net()],
        tracks=[Track("T1", Point(0, 0), Point(2, 0), 0.25, "F.Cu", "N1")],
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        '(layer "F.Cu") (net 1) (uuid',
        '(layer "F.Cu") (net 0) (uuid',
        1,
    )
    path.write_text(text, encoding="utf-8")

    audit = validate_kicad_connectivity_roundtrip(board, path, report)

    assert audit["roundtrip_equal"] is False
    assert audit["source_connectivity_complete"] is True
    assert audit["source_equivalent"] is False
    assert audit["tracks"]["equal"] is False
    assert audit["tracks"]["missing"][0]["net"] == {"code": 1, "name": "GND"}
    assert audit["tracks"]["unexpected"][0]["net"] == {"code": 0, "name": ""}


def test_kicad_connectivity_roundtrip_fallback_respects_track_layer_policy(tmp_path):
    board = BoardModel(
        nets=[_net()],
        tracks=[
            Track("T_OK", Point(0, 0), Point(2, 0), 0.25, "F.Cu", "N1"),
            Track("T_BAD_LAYER", Point(0, 1), Point(2, 1), 0.25, "In31.Cu", "N1"),
        ],
    )

    path, _report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    audit = validate_kicad_connectivity_roundtrip(board, path)

    assert audit["roundtrip_equal"] is True
    assert audit["losses"]["skipped_track_ids"] == ["T_BAD_LAYER"]
    assert audit["source_connectivity_complete"] is False
