from photonx_eda_pcb.excellon_routing import RoutedPath
from photonx_eda_pcb.gui.viewport import board_bounds, fit_view, zoom_about
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.models import (
    BoardModel,
    CopperRegion,
    DrillHit,
    OutlineSegment,
    PadCandidate,
    Point,
    Track,
)


def test_board_bounds_covers_every_gui_geometry_type():
    cases = [
        (
            BoardModel(
                tracks=[Track("t", Point(0, 0), Point(10, 0), 2, "F.Cu")]
            ),
            (-1.0, -1.0, 11.0, 1.0),
        ),
        (
            BoardModel(
                pads=[PadCandidate("p", Point(5, 5), 4, 2, "rect", "F.Cu")]
            ),
            (3.0, 4.0, 7.0, 6.0),
        ),
        (
            BoardModel(drills=[DrillHit("d", Point(5, 5), 2)]),
            (4.0, 4.0, 6.0, 6.0),
        ),
        (
            BoardModel(
                outline=[OutlineSegment("o", Point(-1, -2), Point(3, 4))]
            ),
            (-1.0, -2.0, 3.0, 4.0),
        ),
        (
            BoardModel(slots=[SlotFeature("s", (0, 0), (10, 0), 2)]),
            (-1.0, -1.0, 11.0, 1.0),
        ),
        (
            BoardModel(routes=[RoutedPath("r", ((0, 0), (10, 10)), 4)]),
            (-2.0, -2.0, 12.0, 12.0),
        ),
        (
            BoardModel(
                regions=[
                    CopperRegion(
                        "g",
                        (Point(0, 0), Point(3, 0), Point(3, 4), Point(0, 4)),
                        "F.Cu",
                    )
                ]
            ),
            (0.0, 0.0, 3.0, 4.0),
        ),
    ]

    for board, expected in cases:
        assert board_bounds(board) == expected


def test_board_bounds_empty_board_is_none():
    assert board_bounds(BoardModel()) is None


def test_fit_view_centers_and_fits_bounds_with_padding():
    scale, offset_x, offset_y = fit_view((10, 20, 30, 40), 240, 140, padding=20)

    assert scale == 5.0
    assert offset_x == 20.0
    assert offset_y == -80.0
    assert offset_x + 10 * scale == 70.0
    assert offset_x + 30 * scale == 170.0
    assert offset_y + 20 * scale == 20.0
    assert offset_y + 40 * scale == 120.0


def test_zoom_about_preserves_board_point_under_cursor():
    scale, offset_x, offset_y = zoom_about(10, 20, 30, 120, 80, 2)

    assert scale == 20.0
    assert offset_x == -80.0
    assert offset_y == -20.0
    assert offset_x + 10 * scale == 120.0
    assert offset_y + 5 * scale == 80.0
