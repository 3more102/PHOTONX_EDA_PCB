from photonx_eda_pcb.excellon_routing.model import RoutedPath
from photonx_eda_pcb.gui.viewport import board_bounds, fit_viewport
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


def test_board_bounds_cover_all_renderable_evidence():
    board = BoardModel(
        tracks=[
            Track(
                "T1",
                Point(0, 0),
                Point(10, 0),
                width=2,
                layer="F.Cu",
            )
        ],
        pads=[
            PadCandidate(
                "P1",
                Point(20, 5),
                size_x=4,
                size_y=6,
                shape="oval",
                layer="F.Cu",
            )
        ],
        drills=[DrillHit("D1", Point(-5, -5), diameter=2)],
        outline=[OutlineSegment("O1", Point(-10, 3), Point(-8, 4))],
        slots=[
            SlotFeature(
                "S1",
                start=(30, -2),
                end=(40, -2),
                width_mm=4,
            )
        ],
        routes=[
            RoutedPath(
                "R1",
                points=((1, 20), (3, 22)),
                width_mm=2,
            )
        ],
        regions=[
            CopperRegion(
                "G1",
                points=(Point(50, 1), Point(60, 1), Point(60, 5)),
                layer="F.Cu",
                holes=((Point(58, 2), Point(59, 2), Point(59, 3)),),
            )
        ],
    )

    assert board_bounds(board) == (-10, -6, 60, 23)


def test_fit_viewport_centers_board_with_padding():
    board = BoardModel(
        outline=[OutlineSegment("O1", Point(0, 0), Point(10, 20))]
    )

    fitted = fit_viewport(board, 220, 220, padding=10)

    assert fitted == (10.0, 60.0, 10.0)


def test_fit_viewport_can_zoom_below_legacy_two_x_floor():
    board = BoardModel(
        outline=[OutlineSegment("O1", Point(0, 0), Point(1000, 2000))]
    )

    fitted = fit_viewport(board, 220, 220, padding=10)

    assert fitted == (0.1, 60.0, 10.0)


def test_empty_board_has_no_bounds_or_fit():
    board = BoardModel()

    assert board_bounds(board) is None
    assert fit_viewport(board, 800, 600) is None
