from photonx_eda_pcb.excellon_routing import (
    RoutedPath,
    assess_route_export_readiness,
    route_export_descriptor,
)
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.models import BoardModel, NetGroup, PadCandidate, Point
from photonx_eda_pcb.plated_slot_inference import infer_plated_slot_padstack


X2_FOUR_LAYER = {
    "x2_copper_stackup": {
        "status": "declared",
        "layers": ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"],
        "declared_copper_count": 4,
    }
}


def _pad(pad_id, layer, *, net_id="N1"):
    return PadCandidate(
        pad_id,
        Point(2.0, 0.0),
        6.0,
        2.0,
        "O",
        layer,
        net_id=net_id,
    )


def _slot_board(layers, *, metadata=None):
    slot = SlotFeature("S", (0.0, 0.0), (4.0, 0.0), 1.0, "plated")
    board = BoardModel(
        pads=[_pad(f"P{index}", layer) for index, layer in enumerate(layers)],
        slots=[slot],
        metadata=dict(metadata or {}),
    )
    return board, slot


def _route_board(layers):
    route = RoutedPath(
        "R",
        ((0.0, 0.0), (4.0, 0.0)),
        1.0,
        plated="plated",
    )
    pads = [_pad(f"P{index}", layer) for index, layer in enumerate(layers)]
    board = BoardModel(
        pads=pads,
        routes=[route],
        nets=[NetGroup("N1", [pad.id for pad in pads], 0.99, "SIG")],
        metadata=dict(X2_FOUR_LAYER),
    )
    return board, route


def test_non_copper_pad_does_not_count_as_multilayer_slot_evidence():
    board, slot = _slot_board(["F.Cu", "F.Mask"])

    result = infer_plated_slot_padstack(board, slot)

    assert result.padstack is None
    assert "SLOT_PADSTACK_NEEDS_MULTILAYER_EVIDENCE" in result.blockers


def test_x2_declared_stackup_requires_every_copper_layer_for_plated_slot():
    board, slot = _slot_board(
        ["F.Cu", "B.Cu"],
        metadata=X2_FOUR_LAYER,
    )

    result = infer_plated_slot_padstack(board, slot)

    assert result.padstack is None
    assert "SLOT_X2_COPPER_LAYER_COVERAGE_MISMATCH" in result.blockers


def test_x2_complete_plated_slot_preserves_declared_copper_order():
    board, slot = _slot_board(
        ["B.Cu", "In2.Cu", "F.Cu", "In1.Cu"],
        metadata=X2_FOUR_LAYER,
    )

    result = infer_plated_slot_padstack(board, slot)

    assert result.padstack is not None, result.blockers
    assert result.padstack.layers == ("F.Cu", "In1.Cu", "In2.Cu", "B.Cu")
    assert "x2_declared_copper_coverage" in result.padstack.evidence


def test_plated_route_fails_closed_when_x2_inner_copper_support_is_missing():
    board, route = _route_board(["F.Cu", "B.Cu"])

    readiness = assess_route_export_readiness(board.routes, board)

    assert readiness.exportable == ()
    assert readiness.omitted == ("R",)
    assert readiness.reasons["R"] == "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"
    assert route_export_descriptor(route, board) is None


def test_plated_route_exports_only_with_complete_x2_copper_support():
    board, route = _route_board(["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"])

    readiness = assess_route_export_readiness(board.routes, board)
    descriptor = route_export_descriptor(route, board)

    assert readiness.exportable == ("R",)
    assert readiness.omitted == ()
    assert descriptor is not None
    assert descriptor["kind"] == "plated"
    assert descriptor["layers"] == (
        "F.Cu",
        "In1.Cu",
        "In2.Cu",
        "B.Cu",
        "*.Mask",
    )
    assert descriptor["net_id"] == "N1"
