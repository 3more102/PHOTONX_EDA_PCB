import xml.etree.ElementTree as ET

from photonx_eda_pcb.excellon_routing.model import RoutedPath
from photonx_eda_pcb.exporters.svg import export_svg
from photonx_eda_pcb.geometry.bbox import board_bounds
from photonx_eda_pcb.mechanical_features.model import SlotFeature
from photonx_eda_pcb.models import (
    BoardModel,
    CopperRegion,
    DrillHit,
    OutlineSegment,
    PadCandidate,
    Point,
    Track,
)


def test_board_bounds_include_object_extents_and_route_only_geometry():
    route_board = BoardModel(
        routes=[RoutedPath("R0", ((1.0, 2.0), (3.0, 4.0)), 2.0)]
    )
    route_bounds = board_bounds(route_board)
    assert route_bounds is not None
    assert (route_bounds.min_x, route_bounds.min_y) == (0.0, 1.0)
    assert (route_bounds.max_x, route_bounds.max_y) == (4.0, 5.0)

    pad_board = BoardModel(
        pads=[
            PadCandidate(
                "P0",
                Point(10.0, 20.0),
                4.0,
                6.0,
                "R",
                "F.Cu",
            )
        ]
    )
    pad_bounds = board_bounds(pad_board)
    assert pad_bounds is not None
    assert (pad_bounds.min_x, pad_bounds.min_y) == (8.0, 17.0)
    assert (pad_bounds.max_x, pad_bounds.max_y) == (12.0, 23.0)


def test_svg_exports_all_physical_families_and_region_holes(tmp_path):
    board = BoardModel(
        tracks=[
            Track(
                "T0",
                Point(0.0, 0.0),
                Point(4.0, 0.0),
                0.4,
                "F.Cu",
                'N"1',
            )
        ],
        pads=[
            PadCandidate(
                "P0",
                Point(1.0, 1.0),
                1.0,
                1.0,
                "C",
                "F.Cu",
            )
        ],
        drills=[DrillHit("D0", Point(2.0, 2.0), 0.8)],
        outline=[
            OutlineSegment("O0", Point(-1.0, -1.0), Point(6.0, -1.0))
        ],
        slots=[SlotFeature("S0", (3.0, 1.0), (5.0, 1.0), 0.6)],
        routes=[RoutedPath("R0", ((0.0, 3.0), (2.0, 4.0)), 0.5)],
        regions=[
            CopperRegion(
                "R&1",
                (
                    Point(3.0, 3.0),
                    Point(6.0, 3.0),
                    Point(6.0, 6.0),
                    Point(3.0, 6.0),
                ),
                "B.Cu",
                holes=(
                    (
                        Point(4.0, 4.0),
                        Point(5.0, 4.0),
                        Point(5.0, 5.0),
                        Point(4.0, 5.0),
                    ),
                ),
            )
        ],
    )

    text = export_svg(board, tmp_path / "board.svg").read_text(encoding="utf-8")

    ET.fromstring(text)
    for kind in ("track", "pad", "drill", "outline", "slot", "route", "copper-region"):
        assert f'class="{kind}"' in text

    assert 'fill-rule="evenodd"' in text
    assert 'data-object-id="R&amp;1"' in text
    assert 'data-net-id="N&quot;1"' in text
    assert "<ellipse " in text


def test_region_only_board_gets_nonempty_svg_viewbox(tmp_path):
    board = BoardModel(
        regions=[
            CopperRegion(
                "R0",
                (
                    Point(10.0, 20.0),
                    Point(12.0, 20.0),
                    Point(12.0, 23.0),
                    Point(10.0, 23.0),
                ),
                "F.Cu",
            )
        ]
    )

    text = export_svg(board, tmp_path / "region.svg", padding=1.0).read_text(
        encoding="utf-8"
    )
    assert 'viewBox="9.0 19.0 4.0 5.0"' in text
