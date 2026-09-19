from photonx_eda_pcb.gui.state import EDGE_CUTS_LAYER, ViewState, board_layers
from photonx_eda_pcb.models import (
    BoardModel,
    CopperRegion,
    OutlineSegment,
    PadCandidate,
    Point,
    Track,
)


def _board() -> BoardModel:
    return BoardModel(
        tracks=[
            Track("t1", Point(0, 0), Point(1, 0), 0.2, "F.Cu"),
            Track("t2", Point(0, 1), Point(1, 1), 0.2, "In10.Cu"),
            Track("t3", Point(0, 2), Point(1, 2), 0.2, "In2.Cu"),
        ],
        pads=[
            PadCandidate("p1", Point(0, 0), 1.0, 1.0, "circle", "B.Cu"),
            PadCandidate("p2", Point(2, 0), 1.0, 1.0, "circle", "F.Cu"),
        ],
        regions=[
            CopperRegion(
                "r1",
                (Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)),
                "In1.Cu",
            )
        ],
        outline=[
            OutlineSegment("o1", Point(0, 0), Point(4, 0)),
        ],
    )


def test_board_layers_are_deduplicated_and_copper_ordered():
    assert board_layers(_board()) == (
        "F.Cu",
        "In1.Cu",
        "In2.Cu",
        "In10.Cu",
        "B.Cu",
        EDGE_CUTS_LAYER,
    )


def test_view_state_starts_with_all_discovered_layers_visible():
    state = ViewState(_board())

    assert set(state.available_layers) == state.visible_layers
    assert all(state.is_layer_visible(layer) for layer in state.available_layers)


def test_view_state_layer_selection_can_hide_all_and_reject_unknown_layers():
    state = ViewState(_board())

    state.set_visible_layers({"F.Cu", "In2.Cu", "Unknown.Layer"})
    assert state.visible_layers == {"F.Cu", "In2.Cu"}
    assert state.is_layer_visible("F.Cu")
    assert not state.is_layer_visible("B.Cu")

    state.hide_all_layers()
    assert state.visible_layers == set()

    state.show_all_layers()
    assert state.visible_layers == set(state.available_layers)


def test_explicit_empty_visibility_is_preserved():
    state = ViewState(_board(), visible_layers=set())

    assert state.visible_layers == set()
