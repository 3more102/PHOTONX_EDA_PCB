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
        "file_header",
        "file_structure",
        "board_settings",
        "layer_table",
        "net_table",
        "tracks",
        "vias",
        "track_arcs",
        "board_outline",
        "unexpected_edge_graphics",
        "unexpected_copper_graphics",
        "unexpected_footprint_copper_graphics",
        "unexpected_fabrication_graphics",
        "unexpected_copper_overrides",
        "unexpected_fabrication_overrides",
        "unexpected_pad_properties",
        "unexpected_net_tie_groups",
        "foreign_footprints",
        "recovered_drills",
        "recovered_pads",
        "copper_regions",
        "region_geometry",
        "region_fill_state",
        "region_rules",
        "recovered_slots",
        "slot_geometry",
        "recovered_routes",
    ]
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is True
    assert audit["source_equivalent"] is True
    assert audit["regions"]["equal"] is True
    assert audit["regions"]["expected_count"] == 1
    assert audit["region_fill_state"]["equal"] is True
    assert audit["region_rules"]["equal"] is True
    assert audit["slots"]["equal"] is True
    assert audit["slots"]["expected_count"] == 1
    assert audit["issues"] == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("version", 19990101),
        ("generator", "other_tool"),
        ("version_count", 2),
        ("generator_count", 0),
    ],
)
def test_connectivity_roundtrip_detects_file_header_drift(
    tmp_path,
    field,
    value,
):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["file_header"][field] = value

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["file_header"]["equal"] is False
    assert audit["roundtrip_equal"] is False


def test_reader_preserves_duplicate_header_token_counts():
    readback = read_kicad_board_text(
        """
        (kicad_pcb
          (version 20240108)
          (version 20240109)
          (generator "photonx_eda_pcb")
          (generator "other_tool")
        )
        """
    )

    assert readback["file_header"] == {
        "version": None,
        "generator": None,
        "version_count": 2,
        "generator_count": 2,
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("general_count", 2),
        ("paper_count", 0),
        ("layers_count", 2),
        ("setup_count", 0),
    ],
)
def test_connectivity_roundtrip_detects_singleton_section_drift(
    tmp_path,
    field,
    value,
):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["file_structure"][field] = value

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["file_structure"]["equal"] is False
    assert audit["roundtrip_equal"] is False


def test_reader_preserves_singleton_board_section_counts():
    readback = read_kicad_board_text(
        """
        (kicad_pcb
          (general (thickness 1.6))
          (general (thickness 2.0))
          (paper "A4")
          (layers (0 "F.Cu" signal))
          (layers (31 "B.Cu" signal))
          (setup (pad_to_mask_clearance 0))
        )
        """
    )

    assert readback["file_structure"] == {
        "general_count": 2,
        "paper_count": 1,
        "paper": "A4",
        "layers_count": 2,
        "setup_count": 1,
    }


def test_reader_preserves_exact_paper_value():
    readback = read_kicad_board_text(
        """
        (kicad_pcb
          (paper "A3")
        )
        """
    )

    assert readback["file_structure"]["paper_count"] == 1
    assert readback["file_structure"]["paper"] == "A3"


def test_reader_rejects_ambiguous_paper_value():
    readback = read_kicad_board_text(
        """
        (kicad_pcb
          (paper "A4")
          (paper "A3")
        )
        """
    )

    assert readback["file_structure"]["paper_count"] == 2
    assert readback["file_structure"]["paper"] is None


def test_connectivity_roundtrip_detects_paper_value_drift(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["file_structure"]["paper"] = "A3"

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["file_structure"]["equal"] is False
    assert audit["roundtrip_equal"] is False
    assert audit["file_structure"]["missing"][0]["paper"] == "A4"
    assert audit["file_structure"]["unexpected"][0]["paper"] == "A3"


def test_reader_exposes_board_and_footprint_fabrication_graphics():
    readback = read_kicad_board_text(
        """
        (kicad_pcb
          (gr_rect
            (start 0 0)
            (end 2 2)
            (stroke (width 0.1) (type default))
            (fill none)
            (layer "F.Mask")
            (uuid 00000000-0000-0000-0000-000000000081)
          )
          (footprint "PHOTONX:RecoveredPad"
            (layer "F.Cu")
            (uuid 00000000-0000-0000-0000-000000000082)
            (at 0 0)
            (property "Reference" "P1"
              (at 0 -2 0)
              (layer "F.SilkS")
              hide
              (uuid 00000000-0000-0000-0000-000000000083)
            )
            (fp_line
              (start 0 0)
              (end 1 0)
              (stroke (width 0.1) (type default))
              (layer "B.Paste")
              (uuid 00000000-0000-0000-0000-000000000084)
            )
          )
        )
        """
    )

    assert readback["unexpected_fabrication_graphics"] == [
        {
            "type": "gr_rect",
            "layer": "F.Mask",
            "uuid": "00000000-0000-0000-0000-000000000081",
            "root_index": 0,
        }
    ]
    assert readback["footprints"][0]["unexpected_fabrication_graphics"] == [
        {
            "type": "fp_line",
            "layer": "B.Paste",
            "uuid": "00000000-0000-0000-0000-000000000084",
            "child_index": 4,
        }
    ]


def test_connectivity_roundtrip_rejects_direct_fabrication_graphics():
    readback = read_kicad_board_text(
        """
        (kicad_pcb
          (gr_circle
            (center 0 0)
            (end 1 0)
            (stroke (width 0.1) (type default))
            (fill solid)
            (layer "F.Paste")
            (uuid 00000000-0000-0000-0000-000000000085)
          )
        )
        """
    )

    audit = compare_kicad_connectivity(BoardModel(), readback)

    assert audit["unexpected_fabrication_graphics"]["equal"] is False
    assert audit["unexpected_fabrication_graphics"]["observed_count"] == 1
    assert audit["unexpected_fabrication_graphics"]["unexpected"][0] == {
        "scope": "board",
        "footprint_name": None,
        "reference": None,
        "type": "gr_circle",
        "layer": "F.Paste",
        "uuid": "00000000-0000-0000-0000-000000000085",
    }
    assert audit["roundtrip_equal"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("aux_axis_origin", (10.0, 20.0)),
        ("grid_origin", (1.5, 2.5)),
        ("pcbplotparams_present", True),
    ],
)
def test_connectivity_roundtrip_rejects_unexpected_setup_output_controls(
    tmp_path,
    field,
    value,
):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["board_settings"][field] = value

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["board_settings"]["equal"] is False
    assert audit["roundtrip_equal"] is False


def test_reader_preserves_setup_origins_and_plot_settings_presence():
    readback = read_kicad_board_text(
        """
        (kicad_pcb
          (setup
            (pad_to_mask_clearance 0)
            (aux_axis_origin 10 20)
            (grid_origin 1.5 2.5)
            (pcbplotparams
              (outputdirectory "fab")
            )
          )
        )
        """
    )

    assert readback["board_settings"]["aux_axis_origin"] == (10.0, 20.0)
    assert readback["board_settings"]["grid_origin"] == (1.5, 2.5)
    assert readback["board_settings"]["pcbplotparams_present"] is True


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("thickness_count", 2),
        ("pad_to_mask_clearance_count", 2),
    ],
)
def test_connectivity_roundtrip_rejects_duplicate_required_setting_tokens(
    tmp_path,
    field,
    value,
):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["board_settings"][field] = value

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["board_settings"]["equal"] is False
    assert audit["roundtrip_equal"] is False


def test_reader_counts_duplicate_required_setting_tokens():
    readback = read_kicad_board_text(
        """
        (kicad_pcb
          (general
            (thickness 1.6)
            (thickness 2.0)
          )
          (setup
            (pad_to_mask_clearance 0)
            (pad_to_mask_clearance 0.2)
          )
        )
        """
    )

    assert readback["board_settings"]["thickness_count"] == 2
    assert (
        readback["board_settings"]["pad_to_mask_clearance_count"]
        == 2
    )


def test_connectivity_roundtrip_detects_board_thickness_drift(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["board_settings"]["thickness"] = 2.0

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["board_settings"]["equal"] is False
    assert audit["board_settings"]["missing"][0]["thickness"] == 1.6
    assert audit["board_settings"]["unexpected"][0]["thickness"] == 2.0
    assert audit["roundtrip_equal"] is False


def test_connectivity_roundtrip_detects_pad_to_mask_clearance_drift(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["board_settings"]["pad_to_mask_clearance"] = 0.2

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["board_settings"]["equal"] is False
    assert (
        audit["board_settings"]["missing"][0]["pad_to_mask_clearance"]
        == 0.0
    )
    assert (
        audit["board_settings"]["unexpected"][0]["pad_to_mask_clearance"]
        == 0.2
    )
    assert audit["roundtrip_equal"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("solder_mask_min_width", 0.1),
        ("pad_to_paste_clearance", -0.05),
        ("pad_to_paste_clearance_ratio", 90.0),
        ("stackup_present", True),
    ],
)
def test_connectivity_roundtrip_rejects_unexpected_manufacturing_settings(
    tmp_path,
    field,
    value,
):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["board_settings"][field] = value

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["board_settings"]["equal"] is False
    assert audit["roundtrip_equal"] is False
    assert audit["board_settings"]["unexpected"][0][field] == value


def test_kicad_reader_preserves_optional_manufacturing_settings():
    text = """
    (kicad_pcb
      (general (thickness 1.6))
      (setup
        (stackup)
        (pad_to_mask_clearance 0)
        (solder_mask_min_width 0.1)
        (pad_to_paste_clearance -0.05)
        (pad_to_paste_clearance_ratio 90)
      )
    )
    """
    readback = read_kicad_board_text(text)

    assert readback["board_settings"] == {
        "thickness": 1.6,
        "thickness_count": 1,
        "pad_to_mask_clearance": 0.0,
        "pad_to_mask_clearance_count": 1,
        "solder_mask_min_width": 0.1,
        "pad_to_paste_clearance": -0.05,
        "pad_to_paste_clearance_ratio": 90.0,
        "aux_axis_origin": None,
        "grid_origin": None,
        "pcbplotparams_present": False,
        "stackup_present": True,
    }


def test_connectivity_roundtrip_exports_exact_proven_via_span(tmp_path):
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

    assert len(readback["vias"]) == 1
    assert readback["vias"][0]["type"] == "through"
    assert readback["vias"][0]["layers"] == ("F.Cu", "B.Cu")
    assert readback["vias"][0]["net"] == 1
    assert report.exported_via_spans == 1
    assert report.exported_via_span_ids == ["D1"]
    assert report.skipped_via_spans == 0
    assert report.skipped_via_span_ids == []
    assert audit["vias"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is True
    assert audit["source_equivalent"] is True
    assert audit["losses"]["omitted_proven_via_span_drill_ids"] == []


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


def test_connectivity_roundtrip_rejects_top_level_copper_graphic():
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
      (gr_line
        (start 0 0)
        (end 5 0)
        (stroke (width 0.4) (type default))
        (layer "F.Cu")
        (uuid 00000000-0000-0000-0000-000000000095)
      )
    )
    """
    readback = read_kicad_board_text(text)

    audit = compare_kicad_connectivity(BoardModel(), readback)

    assert audit["roundtrip_equal"] is False
    assert audit["unexpected_copper_graphics"]["equal"] is False
    assert audit["unexpected_copper_graphics"]["observed_count"] == 1
    assert audit["unexpected_copper_graphics"]["unexpected"] == [
        {
            "type": "gr_line",
            "layer": "F.Cu",
            "uuid": "00000000-0000-0000-0000-000000000095",
        }
    ]


def test_connectivity_roundtrip_rejects_non_gr_copper_item():
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
      (dimension
        (type aligned)
        (layer "F.Cu")
        (uuid 00000000-0000-0000-0000-000000000092)
      )
    )
    """
    readback = read_kicad_board_text(text)

    audit = compare_kicad_connectivity(BoardModel(), readback)

    assert audit["roundtrip_equal"] is False
    assert audit["unexpected_copper_graphics"]["observed_count"] == 1
    assert audit["unexpected_copper_graphics"]["unexpected"] == [
        {
            "type": "dimension",
            "layer": "F.Cu",
            "uuid": "00000000-0000-0000-0000-000000000092",
        }
    ]


def test_connectivity_roundtrip_rejects_footprint_copper_graphic(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    footprint = next(
        item
        for item in readback["footprints"]
        if item["name"] == "PHOTONX:RecoveredPad"
    )
    footprint["unexpected_copper_graphics"].append(
        {
            "type": "fp_poly",
            "layer": "F.Cu",
            "uuid": "00000000-0000-0000-0000-000000000093",
        }
    )

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["unexpected_footprint_copper_graphics"]["equal"] is False
    assert (
        audit["unexpected_footprint_copper_graphics"]["observed_count"]
        == 1
    )
    assert audit["unexpected_footprint_copper_graphics"]["unexpected"][0] == {
        "footprint_name": "PHOTONX:RecoveredPad",
        "reference": "P1",
        "type": "fp_poly",
        "layer": "F.Cu",
        "uuid": "00000000-0000-0000-0000-000000000093",
    }


def test_connectivity_roundtrip_rejects_footprint_copper_override(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    footprint = next(
        item
        for item in readback["footprints"]
        if item["name"] == "PHOTONX:RecoveredPad"
    )
    footprint["copper_overrides"]["zone_connect"] = 2

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["unexpected_copper_overrides"]["observed_count"] == 1
    assert audit["unexpected_copper_overrides"]["unexpected"][0] == {
        "scope": "footprint",
        "footprint_name": "PHOTONX:RecoveredPad",
        "reference": "P1",
        "pad_number": None,
        "overrides": {"zone_connect": 2},
    }


def test_connectivity_roundtrip_rejects_pad_copper_override(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    footprint = next(
        item
        for item in readback["footprints"]
        if item["name"] == "PHOTONX:RecoveredPad"
    )
    footprint["pads"][0]["copper_overrides"]["thermal_gap"] = 0.2

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["unexpected_copper_overrides"]["observed_count"] == 1
    assert audit["unexpected_copper_overrides"]["unexpected"][0] == {
        "scope": "pad",
        "footprint_name": "PHOTONX:RecoveredPad",
        "reference": "P1",
        "pad_number": "1",
        "overrides": {"thermal_gap": 0.2},
    }


@pytest.mark.parametrize(
    ("scope", "field", "value"),
    [
        ("footprint", "solder_mask_margin", 0.1),
        ("footprint", "solder_paste_margin", -0.05),
        ("footprint", "solder_paste_ratio", 0.9),
        ("pad", "solder_mask_margin", 0.1),
        ("pad", "solder_paste_margin", -0.05),
        ("pad", "solder_paste_margin_ratio", 0.9),
    ],
)
def test_connectivity_roundtrip_rejects_fabrication_overrides(
    tmp_path,
    scope,
    field,
    value,
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
        if footprint["name"] == "PHOTONX:RecoveredPad"
    )
    if scope == "footprint":
        target["fabrication_overrides"][field] = value
    else:
        target["pads"][0]["fabrication_overrides"][field] = value

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["unexpected_fabrication_overrides"]["equal"] is False
    assert audit["unexpected_fabrication_overrides"]["observed_count"] == 1
    assert (
        audit["unexpected_fabrication_overrides"]["unexpected"][0][
            "overrides"
        ][field]
        == value
    )


def test_connectivity_roundtrip_rejects_photonx_pad_property(tmp_path):
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
    target["pads"][0]["property"] = "pad_prop_castellated"

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["unexpected_pad_properties"]["equal"] is False
    assert audit["unexpected_pad_properties"]["observed_count"] == 1
    assert audit["unexpected_pad_properties"]["unexpected"][0]["property"] == (
        "pad_prop_castellated"
    )


def test_connectivity_roundtrip_rejects_photonx_net_tie_groups(tmp_path):
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
    target["net_tie_pad_groups"] = ("1,2",)

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["unexpected_net_tie_groups"]["equal"] is False
    assert audit["unexpected_net_tie_groups"]["observed_count"] == 1
    assert audit["unexpected_net_tie_groups"]["unexpected"][0]["groups"] == [
        "1,2"
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


@pytest.mark.parametrize(
    ("field", "value"),
    [
        (
            "reference_uuid",
            "00000000-0000-0000-0000-000000000080",
        ),
        ("reference_count", 2),
    ],
)
def test_connectivity_roundtrip_detects_reference_identity_drift(
    tmp_path,
    field,
    value,
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
        if footprint["name"] == "PHOTONX:RecoveredPad"
    )
    target[field] = value

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["pads"]["equal"] is False


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


def test_connectivity_roundtrip_detects_region_fill_state_drift(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    zone = readback["zones"][0]
    assert zone["fill_enabled"] is True
    assert len(zone["filled_polygons"]) == 1
    zone["fill_enabled"] = False

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["regions"]["equal"] is True
    assert audit["region_geometry"]["equal"] is True
    assert audit["region_fill_state"]["equal"] is False
    assert audit["roundtrip_equal"] is False


def test_connectivity_roundtrip_detects_region_fill_cache_drift(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    zone = readback["zones"][0]
    zone["filled_polygons"] = ()

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["regions"]["equal"] is True
    assert audit["region_geometry"]["equal"] is True
    assert audit["region_fill_state"]["equal"] is False
    assert audit["region_fill_state"]["missing"][0]["filled_polygons"]
    assert audit["roundtrip_equal"] is False


def test_connectivity_roundtrip_preserves_holed_region_fill_policy(tmp_path):
    board = BoardModel(
        regions=[
            CopperRegion(
                "RH",
                (
                    Point(0, 0),
                    Point(6, 0),
                    Point(6, 6),
                    Point(0, 6),
                ),
                "F.Cu",
                holes=(
                    (
                        Point(2, 2),
                        Point(4, 2),
                        Point(4, 4),
                        Point(2, 4),
                    ),
                ),
            )
        ]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    zone = readback["zones"][0]
    assert zone["fill_enabled"] is False
    assert zone["filled_polygons"] == ()

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["region_geometry"]["equal"] is True
    assert audit["region_fill_state"]["equal"] is True
    assert audit["roundtrip_equal"] is True


def test_connectivity_roundtrip_detects_region_rule_drift(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    zone = readback["zones"][0]
    zone["rules"]["connect_clearance"] = 0.75

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["regions"]["equal"] is True
    assert audit["region_geometry"]["equal"] is True
    assert audit["region_fill_state"]["equal"] is True
    assert audit["region_rules"]["equal"] is False
    assert audit["region_rules"]["missing"][0]["connect_clearance"] == 0.5
    assert audit["region_rules"]["unexpected"][0]["connect_clearance"] == 0.75
    assert audit["roundtrip_equal"] is False


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("priority", 4),
        ("hatch_style", "full"),
        ("hatch_pitch", 0.75),
        ("keepout", True),
        ("connect_type", "full"),
        ("fill_mode", "hatched"),
        ("filled_areas_thickness", False),
        ("smoothing", "fillet"),
        ("smoothing_radius", 0.2),
        ("island_area_min", 1.0),
        ("hatch_thickness", 0.2),
        ("hatch_gap", 0.6),
        ("hatch_orientation", 30.0),
        ("hatch_smoothing_level", 2),
        ("hatch_smoothing_value", 0.4),
        ("hatch_border_algorithm", 1),
        ("hatch_min_hole_area", 0.8),
    ],
)
def test_connectivity_roundtrip_detects_region_semantic_rule_drift(
    tmp_path,
    key,
    value,
):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["zones"][0]["rules"][key] = value

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["region_rules"]["equal"] is False
    assert audit["roundtrip_equal"] is False


def test_connectivity_roundtrip_detects_region_thermal_rule_drift(tmp_path):
    board = _board_with_all_connectivity_families()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    zone = readback["zones"][0]
    zone["rules"]["thermal_gap"] = 0.9

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["region_rules"]["equal"] is False
    assert audit["region_rules"]["missing"][0]["thermal_gap"] == 0.5
    assert audit["region_rules"]["unexpected"][0]["thermal_gap"] == 0.9
    assert audit["roundtrip_equal"] is False


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
        "ambiguous_net_ids": [],
        "duplicate_object_ids": [],
        "skipped_drill_ids": [],
        "skipped_outline_ids": [],
        "skipped_pad_ids": [],
        "skipped_track_ids": ["T_SKIP"],
        "skipped_region_ids": ["R_SKIP"],
        "skipped_slot_ids": ["S_SKIP"],
        "unresolved_pad_net_ids": ["P_UNRESOLVED"],
        "unresolved_slot_net_ids": [],
        "omitted_route_ids": [],
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


def test_connectivity_roundtrip_marks_unsupported_pad_shape_as_source_loss(
    tmp_path,
):
    board = BoardModel(
        pads=[
            PadCandidate(
                "P_BAD_SHAPE",
                Point(1, 2),
                2,
                1,
                "X",
                "F.Cu",
            )
        ]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    audit = compare_kicad_connectivity(board, readback, report)

    assert report.skipped_pad_ids == ["P_BAD_SHAPE"]
    assert audit["pads"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
    assert audit["losses"]["skipped_pad_ids"] == ["P_BAD_SHAPE"]


def test_connectivity_roundtrip_marks_drilled_pad_as_source_loss(tmp_path):
    board = BoardModel(
        pads=[
            PadCandidate(
                "P_DRILLED",
                Point(1, 2),
                2,
                2,
                "C",
                "F.Cu",
                drill=0.8,
            )
        ]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    audit = compare_kicad_connectivity(board, readback, report)

    assert report.skipped_pad_ids == ["P_DRILLED"]
    assert audit["pads"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
    assert audit["losses"]["skipped_pad_ids"] == ["P_DRILLED"]


def test_duplicate_track_ids_are_omitted_before_uuid_generation(
    tmp_path,
):
    board = BoardModel(
        tracks=[
            Track(
                "T_DUP",
                Point(0, 0),
                Point(2, 0),
                0.25,
                "F.Cu",
            ),
            Track(
                "T_DUP",
                Point(0, 1),
                Point(2, 1),
                0.25,
                "F.Cu",
            ),
        ]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    audit = compare_kicad_connectivity(board, readback, report)

    assert readback["segments"] == []
    assert report.exported_track_ids == []
    assert report.skipped_tracks == 2
    assert report.skipped_track_ids == ["T_DUP"]
    assert report.ok is False
    assert any(
        issue.code == "KICAD_OBJECT_ID_DUPLICATE"
        and issue.object_id == "T_DUP"
        for issue in report.issues
    )
    assert audit["tracks"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
    assert audit["losses"]["duplicate_object_ids"] == ["T_DUP"]
    assert audit["losses"]["skipped_track_ids"] == ["T_DUP"]


def test_duplicate_source_net_ids_fail_closed_without_last_one_wins(
    tmp_path,
):
    board = BoardModel(
        nets=[
            NetGroup("N_DUP", [], 1.0, "FIRST"),
            NetGroup("N_DUP", [], 1.0, "SECOND"),
            NetGroup("N_OK", [], 1.0, "SIG"),
        ],
        tracks=[
            Track(
                "T_DUP",
                Point(0, 0),
                Point(2, 0),
                0.25,
                "F.Cu",
                "N_DUP",
            ),
            Track(
                "T_OK",
                Point(0, 1),
                Point(2, 1),
                0.25,
                "F.Cu",
                "N_OK",
            ),
        ],
        pads=[
            PadCandidate(
                "P_DUP",
                Point(1, 2),
                1.0,
                1.0,
                "C",
                "F.Cu",
                None,
                "N_DUP",
            )
        ],
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    audit = compare_kicad_connectivity(board, readback, report)

    assert readback["nets"] == [
        {"code": 0, "name": ""},
        {"code": 1, "name": "SIG"},
    ]
    assert report.ok is False
    assert any(
        issue.code == "KICAD_NET_ID_DUPLICATE"
        and issue.object_id == "N_DUP"
        for issue in report.issues
    )
    assert report.skipped_track_ids == ["T_DUP"]
    assert audit["nets"]["equal"] is True
    assert audit["tracks"]["equal"] is True
    assert audit["pads"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
    assert audit["losses"]["ambiguous_net_ids"] == ["N_DUP"]
    assert audit["losses"]["skipped_track_ids"] == ["T_DUP"]
    assert audit["losses"]["unresolved_pad_net_ids"] == ["P_DUP"]


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
