from pathlib import Path

import pytest

from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.models import BoardModel, CopperRegion, NetGroup, Point
from photonx_eda_pcb.roundtrip import compare_kicad_copper_regions


def _ring(*coords):
    return tuple(Point(x, y) for x, y in coords)


def _board_with_holed_region():
    return BoardModel(
        regions=[
            CopperRegion(
                "R1",
                _ring((0, 0), (4, 0), (4, 3), (0, 3), (0, 0)),
                "F.Cu",
                net_id="N1",
                holes=(
                    _ring((1, 1), (2, 1), (2, 2), (1, 2), (1, 1)),
                ),
            )
        ],
        nets=[NetGroup("N1", ["R1"], 1.0, label="GND")],
    )


def test_kicad_reader_exposes_zone_shell_holes_and_identity(tmp_path: Path):
    board = _board_with_holed_region()
    path, report = export_kicad_with_report(board, tmp_path / "zones.kicad_pcb")

    parsed = read_kicad_board_text(path.read_text(encoding="utf-8"))

    assert report.exported_region_ids == ["R1"]
    assert len(parsed["zones"]) == 1
    zone = parsed["zones"][0]
    assert zone["name"] == "PHOTONX:R1"
    assert zone["net"] == 1
    assert zone["net_name"] == "GND"
    assert zone["layer"] == "F.Cu"
    assert zone["layers"] == ()
    assert zone["fill_enabled"] is False
    assert zone["rules"] == {
        "hatch_style": "edge",
        "hatch_pitch": 0.5,
        "priority": 0,
        "keepout": False,
        "connect_type": None,
        "fill_mode": None,
        "filled_areas_thickness": True,
        "connect_clearance": 0.5,
        "min_thickness": 0.25,
        "thermal_gap": None,
        "thermal_bridge_width": None,
        "smoothing": None,
        "smoothing_radius": None,
        "island_removal_mode": None,
        "island_area_min": None,
        "hatch_thickness": None,
        "hatch_gap": None,
        "hatch_orientation": None,
        "hatch_smoothing_level": None,
        "hatch_smoothing_value": None,
        "hatch_border_algorithm": None,
        "hatch_min_hole_area": None,
    }
    assert zone["outline"] == ((0.0, 0.0), (4.0, 0.0), (4.0, 3.0), (0.0, 3.0))
    assert zone["holes"] == (
        ((1.0, 1.0), (2.0, 1.0), (2.0, 2.0), (1.0, 2.0)),
    )
    assert zone["filled_polygons"] == ()


def test_exported_holed_region_roundtrips_semantically(tmp_path: Path):
    board = _board_with_holed_region()
    path, _ = export_kicad_with_report(board, tmp_path / "zones.kicad_pcb")
    parsed = read_kicad_board_text(path.read_text(encoding="utf-8"))

    comparison = compare_kicad_copper_regions(board, parsed["zones"])

    assert comparison["equal"]
    assert comparison["missing"] == []
    assert comparison["unexpected"] == []


def test_exported_solid_region_roundtrips_with_saved_fill(tmp_path: Path):
    board = BoardModel(
        regions=[
            CopperRegion(
                "SOLID",
                _ring((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)),
                "In2.Cu",
            )
        ]
    )
    path, _ = export_kicad_with_report(board, tmp_path / "solid.kicad_pcb")
    parsed = read_kicad_board_text(path.read_text(encoding="utf-8"))

    zone = parsed["zones"][0]
    assert zone["fill_enabled"] is True
    assert zone["rules"] == {
        "hatch_style": "edge",
        "hatch_pitch": 0.5,
        "priority": 0,
        "keepout": False,
        "connect_type": None,
        "fill_mode": None,
        "filled_areas_thickness": True,
        "connect_clearance": 0.5,
        "min_thickness": 0.25,
        "thermal_gap": 0.5,
        "thermal_bridge_width": 0.5,
        "smoothing": None,
        "smoothing_radius": None,
        "island_removal_mode": 1,
        "island_area_min": None,
        "hatch_thickness": None,
        "hatch_gap": None,
        "hatch_orientation": None,
        "hatch_smoothing_level": None,
        "hatch_smoothing_value": None,
        "hatch_border_algorithm": None,
        "hatch_min_hole_area": None,
    }
    assert zone["layer"] == "In2.Cu"
    assert zone["holes"] == ()
    assert zone["filled_polygons"] == (
        {
            "layer": "In2.Cu",
            "points": ((0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (0.0, 1.0)),
        },
    )
    assert compare_kicad_copper_regions(board, parsed["zones"])["equal"]


def test_region_roundtrip_comparison_is_start_and_winding_invariant(tmp_path: Path):
    board = _board_with_holed_region()
    path, _ = export_kicad_with_report(board, tmp_path / "zones.kicad_pcb")
    parsed = read_kicad_board_text(path.read_text(encoding="utf-8"))
    zone = dict(parsed["zones"][0])

    outline = list(zone["outline"])
    outline = outline[2:] + outline[:2]
    zone["outline"] = tuple(reversed(outline))

    hole = list(zone["holes"][0])
    hole = hole[1:] + hole[:1]
    zone["holes"] = (tuple(reversed(hole)),)

    assert compare_kicad_copper_regions(board, [zone])["equal"]


def test_zone_reader_rejects_fractional_net_ordinal():
    text = """
    (kicad_pcb
      (zone
        (net 1.5)
        (net_name "GND")
        (layer "F.Cu")
        (polygon (pts (xy 0 0) (xy 1 0) (xy 0 1)))
      )
    )
    """

    with pytest.raises(ValueError, match="zone net ordinal must be an integer"):
        read_kicad_board_text(text)



def test_zone_reader_exposes_priority_keepout_and_fill_semantics():
    text = """
    (kicad_pcb
      (zone
        (net 0)
        (net_name "")
        (layer "F.Cu")
        (name "PHOTONX:RULE")
        (hatch full 0.75)
        (priority 3)
        (filled_areas_thickness no)
        (keepout
          (tracks not_allowed)
          (vias not_allowed)
          (pads not_allowed)
          (copperpour not_allowed)
          (footprints not_allowed)
        )
        (connect_pads full (clearance 0.4))
        (min_thickness 0.2)
        (fill
          yes
          (mode hatched)
          (thermal_gap 0.3)
          (thermal_bridge_width 0.35)
          (smoothing fillet)
          (radius 0.15)
          (island_removal_mode 2)
          (island_area_min 1.25)
          (hatch_thickness 0.2)
          (hatch_gap 0.6)
          (hatch_orientation 30.0)
          (hatch_smoothing_level 2)
          (hatch_smoothing_value 0.4)
          (hatch_border_algorithm 1)
          (hatch_min_hole_area 0.8)
        )
        (polygon
          (pts
            (xy 0 0)
            (xy 2 0)
            (xy 2 2)
            (xy 0 2)
          )
        )
      )
    )
    """
    zone = read_kicad_board_text(text)["zones"][0]

    assert zone["rules"] == {
        "hatch_style": "full",
        "hatch_pitch": 0.75,
        "priority": 3,
        "keepout": True,
        "connect_type": "full",
        "fill_mode": "hatched",
        "filled_areas_thickness": False,
        "connect_clearance": 0.4,
        "min_thickness": 0.2,
        "thermal_gap": 0.3,
        "thermal_bridge_width": 0.35,
        "smoothing": "fillet",
        "smoothing_radius": 0.15,
        "island_removal_mode": 2,
        "island_area_min": 1.25,
        "hatch_thickness": 0.2,
        "hatch_gap": 0.6,
        "hatch_orientation": 30.0,
        "hatch_smoothing_level": 2,
        "hatch_smoothing_value": 0.4,
        "hatch_border_algorithm": 1,
        "hatch_min_hole_area": 0.8,
    }
