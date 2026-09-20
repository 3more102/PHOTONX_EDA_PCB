import pytest

# KiCad net ordinals are intentionally parsed fail-closed as exact integers.
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.models import (
    BoardModel,
    CopperRegion,
    DrillHit,
    NetGroup,
    OutlineSegment,
    PadCandidate,
    Point,
    Track,
)
from photonx_eda_pcb.roundtrip import compare_kicad_connectivity


def _net():
    return NetGroup("N1", [], 1.0, "GND")


def _board_with_all_connectivity_families():
    return BoardModel(
        nets=[_net()],
        tracks=[
            Track("T1", Point(0, 0), Point(4, 0), 0.25, "F.Cu", "N1"),
        ],
        pads=[
            PadCandidate(
                "P1",
                Point(0, 0),
                1.2,
                1.2,
                "C",
                "F.Cu",
                None,
                "N1",
            ),
        ],
        regions=[
            CopperRegion(
                "R1",
                (
                    Point(1, 1),
                    Point(3, 1),
                    Point(3, 3),
                    Point(1, 3),
                ),
                "F.Cu",
                "N1",
            ),
        ],
        slots=[
            SlotFeature("S1", (5, 0), (7, 0), 1.0, "non-plated"),
        ],
    )


def test_connectivity_roundtrip_covers_regions_and_slots(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["scope"] == [
        "layer_table",
        "net_table",
        "tracks",
        "vias",
        "track_arcs",
        "board_outline",
        "unexpected_edge_graphics",
        "foreign_footprints",
        "recovered_pads",
        "copper_regions",
        "region_geometry",
        "recovered_slots",
        "slot_geometry",
    ]
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is True
    assert audit["source_equivalent"] is True
    assert audit["regions"]["equal"] is True
    assert audit["regions"]["expected_count"] == 1
    assert audit["slots"]["equal"] is True
    assert audit["slots"]["expected_count"] == 1
    assert audit["issues"] == []


def test_connectivity_roundtrip_marks_proven_via_span_as_source_loss(tmp_path):
    board = BoardModel(
        nets=[_net()],
        pads=[
            PadCandidate("P_F", Point(0, 0), 1.0, 1.0, "C", "F.Cu", None, "N1"),
            PadCandidate("P_B", Point(0, 0), 1.0, 1.0, "C", "B.Cu", None, "N1"),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, "plated")],
        metadata={
            "via_spans": [
                {
                    "drill_id": "D1",
                    "from_layer": "F.Cu",
                    "to_layer": "B.Cu",
                    "confidence": 0.95,
                    "proven": True,
                    "pad_ids": ["P_B", "P_F"],
                    "evidence": ["plated drill with two-layer pad support"],
                }
            ]
        },
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    audit = compare_kicad_connectivity(board, readback, report)

    assert readback["vias"] == []
    assert report.skipped_via_spans == 1
    assert report.skipped_via_span_ids == ["D1"]
    assert any(
        issue.code == "KICAD_PROVEN_VIA_SPAN_UNSUPPORTED"
        and issue.object_id == "D1"
        for issue in report.issues
    )
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
    assert audit["losses"]["omitted_proven_via_span_drill_ids"] == ["D1"]


def test_invalid_proven_via_span_metadata_fails_closed(tmp_path):
    board = BoardModel(
        nets=[_net()],
        pads=[
            PadCandidate("P_F", Point(0, 0), 1.0, 1.0, "C", "F.Cu", None, "N1"),
            PadCandidate("P_B", Point(0, 0), 1.0, 1.0, "C", "B.Cu", None, "N1"),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, "unknown")],
        metadata={
            "via_spans": [
                {
                    "drill_id": "D1",
                    "from_layer": "F.Cu",
                    "to_layer": "B.Cu",
                    "confidence": 0.95,
                    "proven": True,
                    "pad_ids": ["P_B", "P_F"],
                    "evidence": [],
                }
            ]
        },
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    audit = compare_kicad_connectivity(board, readback, report)

    assert report.ok is False
    assert report.skipped_via_spans == 0
    assert report.skipped_via_span_ids == []
    assert any(
        issue.code == "KICAD_VIA_SPAN_METADATA_INVALID"
        and issue.object_id == "D1"
        for issue in report.issues
    )
    assert audit["roundtrip_equal"] is False
    assert audit["source_equivalent"] is False
    assert any(
        issue["code"] == "KICAD_ROUNDTRIP_VIA_SPAN_METADATA_INVALID"
        and issue["object_id"] == "D1"
        for issue in audit["issues"]
    )


def test_connectivity_roundtrip_detects_layer_table_drift(tmp_path):
    board = BoardModel(
        tracks=[
            Track(
                "T_IN2",
                Point(0, 0),
                Point(2, 0),
                0.25,
                "In2.Cu",
            )
        ]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["layers"] = [
        row
        for row in readback["layers"]
        if row["name"] != "In1.Cu"
    ]

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["tracks"]["equal"] is True
    assert audit["layer_table"]["equal"] is False
    assert audit["roundtrip_equal"] is False
    assert audit["layer_table"]["missing"] == [
        {"id": 1, "name": "In1.Cu", "type": "signal"}
    ]


def test_connectivity_roundtrip_detects_outline_geometry_drift(tmp_path):
    board = BoardModel(
        outline=[
            OutlineSegment(
                "E1",
                Point(0, 0),
                Point(4, 0),
            )
        ]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    assert readback["edge_lines"] == [((0.0, 0.0), (4.0, 0.0))]
    readback["edge_graphics"][0]["end"] = (5.0, 0.0)

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["outline"]["equal"] is False
    assert audit["roundtrip_equal"] is False
    assert audit["outline"]["missing"][0]["end"] == [4.0, 0.0]
    assert audit["outline"]["unexpected"][0]["end"] == [5.0, 0.0]


def test_connectivity_roundtrip_detects_outline_uuid_drift(tmp_path):
    board = BoardModel(
        outline=[
            OutlineSegment(
                "E1",
                Point(0, 0),
                Point(4, 0),
            )
        ]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["edge_graphics"][0]["uuid"] = (
        "00000000-0000-0000-0000-000000000000"
    )

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["outline"]["equal"] is False
    assert audit["roundtrip_equal"] is False
    assert (
        audit["outline"]["missing"][0]["uuid"]
        != audit["outline"]["unexpected"][0]["uuid"]
    )


def test_connectivity_roundtrip_rejects_non_line_edge_graphic():
    text = """
    (kicad_pcb
      (layers
        (0 "F.Cu" signal)
        (31 "B.Cu" signal)
        (36 "B.SilkS" user "b.silkscreen")
        (37 "F.SilkS" user "f.silkscreen")
        (44 "Edge.Cuts" user)
      )
      (net 0 "")
      (gr_arc
        (start 0 0)
        (mid 1 1)
        (end 2 0)
        (layer "Edge.Cuts")
        (stroke (width 0.1) (type default))
        (uuid 00000000-0000-0000-0000-000000000096)
      )
    )
    """
    readback = read_kicad_board_text(text)

    audit = compare_kicad_connectivity(BoardModel(), readback)

    assert audit["roundtrip_equal"] is False
    assert audit["unexpected_edge_graphics"]["equal"] is False
    assert audit["unexpected_edge_graphics"]["observed_count"] == 1
    assert audit["unexpected_edge_graphics"]["unexpected"] == [
        {
            "type": "gr_arc",
            "uuid": "00000000-0000-0000-0000-000000000096",
        }
    ]


def test_connectivity_roundtrip_rejects_foreign_footprint(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["footprints"].append(
        {
            "name": "Vendor:InjectedPart",
            "reference": "U99",
            "uuid": "00000000-0000-0000-0000-000000000099",
            "at": (10.0, 10.0),
            "angle": 0.0,
            "layer": "F.Cu",
            "pads": [
                {
                    "number": "1",
                    "kind": "smd",
                    "shape": "rect",
                    "layers": ("F.Cu",),
                    "net": 1,
                    "net_name": "GND",
                    "uuid": "00000000-0000-0000-0000-000000000098",
                }
            ],
        }
    )

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["foreign_footprints"]["equal"] is False
    assert audit["foreign_footprints"]["expected_count"] == 0
    assert audit["foreign_footprints"]["observed_count"] == 1
    assert audit["foreign_footprints"]["unexpected"][0]["name"] == (
        "Vendor:InjectedPart"
    )
    assert audit["foreign_footprints"]["unexpected"][0]["pads"][0]["net"] == 1


def test_connectivity_roundtrip_rejects_unexpected_track_arc():
    text = """
    (kicad_pcb
      (layers
        (0 "F.Cu" signal)
        (31 "B.Cu" signal)
        (36 "B.SilkS" user "b.silkscreen")
        (37 "F.SilkS" user "f.silkscreen")
        (44 "Edge.Cuts" user)
      )
      (net 0 "")
      (net 1 "GND")
      (arc
        (start 0 0)
        (mid 1 1)
        (end 2 0)
        (width 0.25)
        (layer "F.Cu")
        (net 1)
        (uuid 00000000-0000-0000-0000-000000000097)
      )
    )
    """
    readback = read_kicad_board_text(text)
    board = BoardModel(nets=[_net()])

    audit = compare_kicad_connectivity(board, readback)

    assert audit["roundtrip_equal"] is False
    assert audit["track_arcs"]["equal"] is False
    assert audit["track_arcs"]["expected_count"] == 0
    assert audit["track_arcs"]["observed_count"] == 1
    assert audit["track_arcs"]["unexpected"][0]["net"] == {
        "code": 1,
        "name": "GND",
    }


def test_kicad_reader_rejects_fractional_track_arc_net_ordinal():
    text = """
    (kicad_pcb
      (arc
        (start 0 0)
        (mid 1 1)
        (end 2 0)
        (width 0.25)
        (layer "F.Cu")
        (net 1.5)
      )
    )
    """
    with pytest.raises(
        ValueError,
        match="track arc net ordinal must be an integer",
    ):
        read_kicad_board_text(text)


def test_connectivity_roundtrip_detects_unexpected_via(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["vias"].append(
        {
            "at": (2.0, 0.0),
            "size": 0.8,
            "drill": 0.4,
            "layers": ("F.Cu", "B.Cu"),
            "net": 1,
        }
    )

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["vias"]["equal"] is False
    assert audit["vias"]["expected_count"] == 0
    assert audit["vias"]["observed_count"] == 1
    assert audit["vias"]["unexpected"][0]["net"] == {
        "code": 1,
        "name": "GND",
    }


def test_connectivity_roundtrip_detects_track_uuid_drift(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["segments"][0]["uuid"] = "00000000-0000-0000-0000-000000000000"

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["tracks"]["equal"] is False
    assert audit["tracks"]["missing"][0]["uuid"] != audit["tracks"]["unexpected"][0]["uuid"]


@pytest.mark.parametrize(
    ("family", "comparison_key"),
    [
        ("pad", "pads"),
        ("region", "regions"),
        ("slot", "slots"),
    ],
)
def test_connectivity_roundtrip_detects_recovered_object_uuid_drift(
    tmp_path,
    family,
    comparison_key,
):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    if family == "pad":
        target = next(
            footprint
            for footprint in readback["footprints"]
            if footprint["name"] == "PHOTONX:RecoveredPad"
        )
    elif family == "region":
        target = readback["zones"][0]
    else:
        target = next(
            footprint
            for footprint in readback["footprints"]
            if footprint["name"] == "PHOTONX:RecoveredNPTHSlot"
        )

    target["uuid"] = "00000000-0000-0000-0000-000000000000"
    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit[comparison_key]["equal"] is False
    assert audit[comparison_key]["missing"][0]["uuid"] != audit[comparison_key]["unexpected"][0]["uuid"]


def test_connectivity_roundtrip_detects_recovered_pad_geometry_drift(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    target = next(
        footprint
        for footprint in readback["footprints"]
        if footprint["name"] == "PHOTONX:RecoveredPad"
    )
    target["pads"][0]["size"] = (9.0, 9.0)

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["pads"]["equal"] is False
    assert audit["pads"]["missing"][0]["geometry"]["size"] == [1.2, 1.2]
    assert audit["pads"]["unexpected"][0]["geometry"]["size"] == [9.0, 9.0]


@pytest.mark.parametrize(
    ("family", "comparison_key"),
    [
        ("pad", "pads"),
        ("slot", "slots"),
    ],
)
def test_connectivity_roundtrip_detects_recovered_child_pad_uuid_drift(
    tmp_path,
    family,
    comparison_key,
):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    target = next(
        footprint
        for footprint in readback["footprints"]
        if footprint["name"]
        == (
            "PHOTONX:RecoveredPad"
            if family == "pad"
            else "PHOTONX:RecoveredNPTHSlot"
        )
    )
    target["pads"][0]["uuid"] = "00000000-0000-0000-0000-000000000000"

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit[comparison_key]["equal"] is False
    assert (
        audit[comparison_key]["missing"][0]["pad_uuid"]
        != audit[comparison_key]["unexpected"][0]["pad_uuid"]
    )


def test_connectivity_roundtrip_detects_region_geometry_drift(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    zone = readback["zones"][0]
    outline = list(zone["outline"])
    outline[0] = (outline[0][0] + 0.5, outline[0][1])
    zone["outline"] = tuple(outline)

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["regions"]["equal"] is True
    assert audit["region_geometry"]["equal"] is False
    assert audit["roundtrip_equal"] is False
    assert audit["region_geometry"]["missing"]
    assert audit["region_geometry"]["unexpected"]


def test_connectivity_roundtrip_detects_zone_net_drift(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["zones"][0]["net"] = 0

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["regions"]["equal"] is False
    assert audit["regions"]["missing"][0]["net"] == {
        "code": 1,
        "name": "GND",
    }
    assert audit["regions"]["unexpected"][0]["net"] == {
        "code": 0,
        "name": "",
    }


def test_connectivity_roundtrip_detects_zone_net_name_drift(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["zones"][0]["net_name"] = "BROKEN"

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert any(
        issue["code"] == "KICAD_ROUNDTRIP_NET_NAME_MISMATCH"
        and issue["object_kind"] == "zone"
        for issue in audit["issues"]
    )


def test_connectivity_roundtrip_detects_slot_geometry_drift(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    observed = readback["mechanical_slots"][0]
    readback["mechanical_slots"][0] = SlotFeature(
        observed.id,
        observed.start,
        observed.end,
        observed.width_mm + 0.25,
        observed.plated,
        observed.tool,
    )

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["slots"]["equal"] is True
    assert audit["slot_geometry"]["equal"] is False
    assert audit["roundtrip_equal"] is False
    assert audit["slot_geometry"]["expected"]
    assert audit["slot_geometry"]["unexpected"]


def test_connectivity_roundtrip_detects_slot_net_claim(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    slot_fp = next(
        footprint
        for footprint in readback["footprints"]
        if footprint["name"] == "PHOTONX:RecoveredNPTHSlot"
    )
    assert slot_fp["reference"] == "S1"
    slot_fp["pads"][0]["net"] = 1

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["slots"]["equal"] is False


def test_connectivity_roundtrip_separates_export_losses(tmp_path):
    board = BoardModel(
        nets=[_net()],
        tracks=[
            Track(
                "T_SKIP",
                Point(0, 0),
                Point(2, 0),
                0.25,
                "F.Cu",
                "MISSING",
            ),
        ],
        pads=[
            PadCandidate(
                "P_UNRESOLVED",
                Point(1, 0),
                1.0,
                1.0,
                "R",
                "F.Cu",
                None,
                "MISSING",
            ),
        ],
        regions=[
            CopperRegion(
                "R_SKIP",
                (
                    Point(3, 1),
                    Point(5, 1),
                    Point(5, 3),
                    Point(3, 3),
                ),
                "F.Cu",
                "MISSING",
            ),
        ],
        slots=[
            SlotFeature("S_SKIP", (6, 0), (8, 0), 1.0, "unknown"),
        ],
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
    assert audit["losses"] == {
        "skipped_pad_ids": [],
        "skipped_track_ids": ["T_SKIP"],
        "skipped_region_ids": ["R_SKIP"],
        "skipped_slot_ids": ["S_SKIP"],
        "unresolved_pad_net_ids": ["P_UNRESOLVED"],
        "unresolved_slot_net_ids": [],
        "omitted_proven_via_span_drill_ids": [],
    }


def test_connectivity_roundtrip_marks_unsupported_pad_layer_as_source_loss(
    tmp_path,
):
    board = BoardModel(
        pads=[
            PadCandidate(
                "P_BAD_LAYER",
                Point(1, 2),
                2,
                1,
                "R",
                "In31.Cu",
            )
        ]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    audit = compare_kicad_connectivity(board, readback, report)

    assert report.skipped_pad_ids == ["P_BAD_LAYER"]
    assert audit["pads"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
    assert audit["losses"]["skipped_pad_ids"] == ["P_BAD_LAYER"]


def test_connectivity_roundtrip_detects_missing_pad_net_name(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    pad_fp = next(
        footprint
        for footprint in readback["footprints"]
        if footprint["name"] == "PHOTONX:RecoveredPad"
    )
    pad_fp["pads"][0]["net_name"] = None

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert any(
        issue["code"] == "KICAD_ROUNDTRIP_NET_NAME_MISMATCH"
        and issue["object_kind"] == "pad"
        for issue in audit["issues"]
    )


def test_kicad_reader_rejects_fractional_net_table_ordinal():
    with pytest.raises(ValueError, match="net table ordinal must be an integer"):
        read_kicad_board_text(
            '(kicad_pcb (net 1.5 "GND"))'
        )


def test_kicad_reader_rejects_fractional_segment_net_ordinal():
    text = """
    (kicad_pcb
      (net 1 "GND")
      (segment
        (start 0 0)
        (end 1 0)
        (width 0.25)
        (layer "F.Cu")
        (net 1.5)
      )
    )
    """
    with pytest.raises(ValueError, match="segment net ordinal must be an integer"):
        read_kicad_board_text(text)


def test_kicad_reader_rejects_fractional_via_net_ordinal():
    text = """
    (kicad_pcb
      (net 1 "GND")
      (via
        (at 0 0)
        (size 0.8)
        (drill 0.4)
        (layers "F.Cu" "B.Cu")
        (net 1.5)
      )
    )
    """
    with pytest.raises(ValueError, match="via net ordinal must be an integer"):
        read_kicad_board_text(text)


def test_kicad_reader_rejects_fractional_pad_net_ordinal():
    text = """
    (kicad_pcb
      (net 1 "GND")
      (footprint "PHOTONX:RecoveredPad"
        (layer "F.Cu")
        (at 0 0)
        (property "Reference" "P1")
        (pad "1" smd circle
          (at 0 0)
          (size 1 1)
          (layers "F.Cu")
          (net 1.5 "GND")
        )
      )
    )
    """
    with pytest.raises(ValueError, match="pad net ordinal must be an integer"):
        read_kicad_board_text(text)
