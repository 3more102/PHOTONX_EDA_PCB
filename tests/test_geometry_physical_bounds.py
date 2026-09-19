import pytest

from photonx_eda_pcb.excellon_routing.model import RoutedPath
from photonx_eda_pcb.geometry.bbox import board_bounds
from photonx_eda_pcb.mechanical_features.model import SlotFeature
from photonx_eda_pcb.models import BoardModel, CopperRegion, DrillHit, Point


def test_board_bounds_include_drill_diameter():
    board=BoardModel(drills=[DrillHit("D1",Point(10.0,-2.0),2.0)])
    bounds=board_bounds(board)
    assert bounds is not None
    assert (bounds.min_x,bounds.max_x)==pytest.approx((9.0,11.0))
    assert (bounds.min_y,bounds.max_y)==pytest.approx((-3.0,-1.0))


def test_board_bounds_include_slots_routes_and_regions():
    board=BoardModel(
        slots=[SlotFeature("S1",(12.0,1.0),(14.0,1.0),2.0)],
        routes=[RoutedPath("R1",((-5.0,-5.0),(-3.0,-4.0)),1.0)],
        regions=[CopperRegion(
            "G1",
            (Point(20.0,20.0),Point(22.0,20.0),Point(22.0,21.0),Point(20.0,21.0)),
            "F.Cu",
        )],
    )
    bounds=board_bounds(board)
    assert bounds is not None
    assert (bounds.min_x,bounds.min_y)==pytest.approx((-5.5,-5.5))
    assert (bounds.max_x,bounds.max_y)==pytest.approx((22.0,21.0))


def test_empty_board_bounds_remain_none():
    assert board_bounds(BoardModel()) is None
