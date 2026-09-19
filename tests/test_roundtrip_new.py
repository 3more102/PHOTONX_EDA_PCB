from photonx_eda_pcb.excellon_routing.model import RoutedPath
from photonx_eda_pcb.models import BoardModel, Point, Track
from photonx_eda_pcb.roundtrip import board_fingerprint, compare_board_models


def test_roundtrip_deterministic():
    a = BoardModel(
        tracks=[Track("t", Point(0, 0), Point(1, 0), 0.2, "F.Cu")]
    )
    b = BoardModel(
        tracks=[Track("t", Point(0, 0), Point(1, 0), 0.2, "F.Cu")]
    )
    assert board_fingerprint(a) == board_fingerprint(b)
    assert compare_board_models(a, b) == []


def test_roundtrip_fingerprint_includes_routed_paths():
    base = RoutedPath(
        id="route-1",
        points=((0.0, 0.0), (1.0, 0.0)),
        width_mm=0.4,
        plated="unknown",
        tool="T01",
    )
    changed = RoutedPath(
        id="route-1",
        points=((0.0, 0.0), (2.0, 0.0)),
        width_mm=0.4,
        plated="unknown",
        tool="T01",
    )

    left = BoardModel(routes=[base])
    right = BoardModel(routes=[changed])

    assert board_fingerprint(left) != board_fingerprint(right)
    assert compare_board_models(left, right) == [
        {"section": "routes", "left_count": 1, "right_count": 1}
    ]


def test_roundtrip_route_order_does_not_change_fingerprint():
    route_a = RoutedPath(
        id="route-a",
        points=((0.0, 0.0), (1.0, 0.0)),
        width_mm=0.3,
        plated="unknown",
        tool="T01",
    )
    route_b = RoutedPath(
        id="route-b",
        points=((2.0, 0.0), (3.0, 0.0)),
        width_mm=0.5,
        plated="plated",
        tool="T02",
    )

    assert board_fingerprint(BoardModel(routes=[route_a, route_b])) == board_fingerprint(
        BoardModel(routes=[route_b, route_a])
    )
