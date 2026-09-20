from photonx_eda_pcb.excellon_routing import (
    RoutedPath,
    assess_route_export_readiness,
    route_export_descriptor,
)
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
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


def _net(pads):
    return NetGroup("N1", [pad.id for pad in pads], 0.99, "SIG")


def test_x2_full_depth_pth_route_exports_on_all_declared_copper_layers():
    route = RoutedPath(
        "R_PTH",
        ((0.0, 0.0), (4.0, 0.0)),
        1.0,
        plated="plated",
        layer_span=("F.Cu", "B.Cu"),
        span_proven=True,
        x2_layer_span=(1, 4),
        x2_span_kind="pth",
    )
    pads = [
        _pad("F", "F.Cu"),
        _pad("I1", "In1.Cu"),
        _pad("I2", "In2.Cu"),
        _pad("B", "B.Cu"),
    ]
    board = BoardModel(
        pads=pads,
        routes=[route],
        nets=[_net(pads)],
        metadata=dict(X2_FOUR_LAYER),
    )

    readiness = assess_route_export_readiness(board.routes, board)
    descriptor = route_export_descriptor(route, board)

    assert readiness.exportable == ("R_PTH",)
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


def test_x2_buried_route_is_preserved_but_not_widened_to_through_hole():
    route = RoutedPath(
        "R_BURIED",
        ((0.0, 0.0), (4.0, 0.0)),
        1.0,
        plated="plated",
        layer_span=("In1.Cu", "In2.Cu"),
        span_proven=True,
        x2_layer_span=(2, 3),
        x2_span_kind="buried",
    )
    pads = [_pad("I1", "In1.Cu"), _pad("I2", "In2.Cu")]
    board = BoardModel(
        pads=pads,
        routes=[route],
        nets=[_net(pads)],
        metadata=dict(X2_FOUR_LAYER),
    )

    readiness = assess_route_export_readiness(board.routes, board)

    assert readiness.exportable == ()
    assert readiness.omitted == ("R_BURIED",)
    assert (
        readiness.reasons["R_BURIED"]
        == "KICAD_PLATED_ROUTE_PARTIAL_DEPTH_UNREPRESENTABLE"
    )
    assert route_export_descriptor(route, board) is None


def test_unresolved_x2_route_span_fails_closed_before_padstack_export():
    route = RoutedPath(
        "R_UNRESOLVED",
        ((0.0, 0.0), (4.0, 0.0)),
        1.0,
        plated="plated",
        layer_span=None,
        span_proven=False,
        x2_layer_span=(1, 2),
        x2_span_kind="blind",
    )
    pads = [_pad("F", "F.Cu"), _pad("I1", "In1.Cu")]
    board = BoardModel(
        pads=pads,
        routes=[route],
        nets=[_net(pads)],
        metadata=dict(X2_FOUR_LAYER),
    )

    readiness = assess_route_export_readiness(board.routes, board)

    assert readiness.exportable == ()
    assert readiness.omitted == ("R_UNRESOLVED",)
    assert (
        readiness.reasons["R_UNRESOLVED"]
        == "KICAD_PLATED_ROUTE_SPAN_UNPROVEN"
    )


def test_partial_x2_slot_padstack_is_inferred_but_kicad_export_fails_closed(
    tmp_path,
):
    slot = SlotFeature(
        "S_BURIED",
        (0.0, 0.0),
        (4.0, 0.0),
        1.0,
        "plated",
        layer_span=("In1.Cu", "In2.Cu"),
        span_proven=True,
        x2_layer_span=(2, 3),
        x2_span_kind="buried",
    )
    pads = [_pad("I1", "In1.Cu"), _pad("I2", "In2.Cu")]
    board = BoardModel(
        pads=pads,
        slots=[slot],
        nets=[_net(pads)],
        metadata=dict(X2_FOUR_LAYER),
    )

    inference = infer_plated_slot_padstack(board, slot)
    assert inference.padstack is not None, inference.blockers
    assert inference.padstack.layers == ("In1.Cu", "In2.Cu")
    assert "x2_proven_layer_span" in inference.padstack.evidence

    path, report = export_kicad_with_report(
        board,
        tmp_path / "partial-slot.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert "RecoveredPlatedSlot" not in text
    assert report.exported_slot_ids == []
    assert report.skipped_slot_ids == ["S_BURIED"]
    assert any(
        issue.code == "KICAD_SLOT_PARTIAL_DEPTH_UNREPRESENTABLE"
        and issue.object_id == "S_BURIED"
        for issue in report.issues
    )
    assert validate_omission_manifest(omission_manifest(report)) == []


def test_full_depth_x2_plated_slot_exports_with_complete_stack(tmp_path):
    slot = SlotFeature(
        "S_PTH",
        (0.0, 0.0),
        (4.0, 0.0),
        1.0,
        "plated",
        layer_span=("F.Cu", "B.Cu"),
        span_proven=True,
        x2_layer_span=(1, 4),
        x2_span_kind="pth",
    )
    pads = [
        _pad("F", "F.Cu"),
        _pad("I1", "In1.Cu"),
        _pad("I2", "In2.Cu"),
        _pad("B", "B.Cu"),
    ]
    board = BoardModel(
        pads=pads,
        slots=[slot],
        nets=[_net(pads)],
        metadata=dict(X2_FOUR_LAYER),
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "full-slot.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert 'footprint "PHOTONX:RecoveredPlatedSlot"' in text
    assert '(layers "F.Cu" "In1.Cu" "In2.Cu" "B.Cu" "*.Mask")' in text
    assert report.exported_slot_ids == ["S_PTH"]
    assert report.skipped_slot_ids == []
