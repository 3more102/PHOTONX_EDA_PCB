from math import inf,nan

from photonx_eda_pcb.checks import run_all_checks
from photonx_eda_pcb.excellon_routing import RoutedPath,validate_route
from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.validation import validate_board
from photonx_eda_pcb.validation_rules import builtin_registry


def _codes(issues):
    return {issue.code for issue in issues}


def test_nonfinite_route_width_is_rejected_across_validation_surfaces():
    route=RoutedPath("R1",((0.0,0.0),(1.0,0.0)),nan)
    board=BoardModel(routes=[route])

    assert "ROUTE_WIDTH_NONFINITE" in validate_route(route)
    assert "ROUTE_WIDTH_NONFINITE" in _codes(validate_board(board).issues)
    assert "ROUTE_WIDTH_INVALID" in _codes(run_all_checks(board))
    assert "ROUTE_WIDTH" in _codes(builtin_registry().run(board))


def test_nonfinite_route_coordinate_is_rejected_across_validation_surfaces():
    route=RoutedPath("R2",((0.0,0.0),(inf,1.0)),0.5)
    board=BoardModel(routes=[route])

    assert "ROUTE_COORDINATE_INVALID" in validate_route(route)
    assert "ROUTE_COORDINATE_INVALID" in _codes(validate_board(board).issues)
    assert "ROUTE_COORDINATE_INVALID" in _codes(run_all_checks(board))
    assert "ROUTE_COORDINATE" in _codes(builtin_registry().run(board))


def test_finite_route_remains_clean_in_route_geometry_validators():
    route=RoutedPath("R3",((0.0,0.0),(1.0,1.0)),0.5)
    board=BoardModel(routes=[route])

    assert validate_route(route)==[]
    assert not ({"ROUTE_WIDTH_NONFINITE","ROUTE_COORDINATE_INVALID"} & _codes(validate_board(board).issues))
    assert not ({"ROUTE_WIDTH_INVALID","ROUTE_COORDINATE_INVALID"} & _codes(run_all_checks(board)))
    assert not ({"ROUTE_WIDTH","ROUTE_COORDINATE"} & _codes(builtin_registry().run(board)))
