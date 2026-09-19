from photonx_eda_pcb.excellon_routing import RoutedPath
from photonx_eda_pcb.models import BoardModel, ComponentHypothesis
from photonx_eda_pcb.roundtrip import board_fingerprint, compare_board_models


def test_route_changes_affect_roundtrip_fingerprint():
    left = BoardModel(routes=[RoutedPath("route-1", ((0, 0), (1, 0)), 0.4)])
    right = BoardModel(routes=[RoutedPath("route-1", ((0, 0), (2, 0)), 0.4)])

    assert board_fingerprint(left) != board_fingerprint(right)
    assert compare_board_models(left, right) == [
        {"section": "routes", "left_count": 1, "right_count": 1}
    ]


def test_component_changes_affect_roundtrip_fingerprint():
    left = BoardModel(
        components=[
            ComponentHypothesis(
                "cmp-1",
                ["pad-1", "pad-2"],
                "resistor_like",
                0.8,
                ["two-pad pattern"],
            )
        ]
    )
    right = BoardModel(
        components=[
            ComponentHypothesis(
                "cmp-1",
                ["pad-1", "pad-2"],
                "capacitor_like",
                0.8,
                ["two-pad pattern"],
            )
        ]
    )

    assert board_fingerprint(left) != board_fingerprint(right)
    assert compare_board_models(left, right) == [
        {"section": "components", "left_count": 1, "right_count": 1}
    ]
