from photonx_eda_pcb.excellon_routing import (
    RoutedPath,
    assess_route_export_readiness,
)
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
from photonx_eda_pcb.exporters.route_omissions import route_omission_manifest
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.models import BoardModel, NetGroup, PadCandidate, Point
from photonx_eda_pcb.roundtrip import validate_kicad_connectivity_roundtrip


def _proven_board(net_a="N1", net_b="N1", include_net=True):
    route = RoutedPath(
        "ROUTE_PTH",
        ((0.0, 0.0), (4.0, 0.0)),
        1.0,
        plated="plated",
    )
    pads = [
        PadCandidate("F", Point(2.0, 0.0), 6.0, 2.0, "O", "F.Cu", net_id=net_a),
        PadCandidate("B", Point(2.0, 0.0), 6.0, 2.0, "O", "B.Cu", net_id=net_b),
    ]
    nets = [NetGroup("N1", ["F", "B"], 0.99, "SIG")] if include_net else []
    return BoardModel(pads=pads, routes=[route], nets=nets), route


def test_source_proven_plated_route_exports_and_roundtrips(tmp_path):
    board, route = _proven_board()

    readiness = assess_route_export_readiness(board.routes, board)
    assert readiness.exportable == ("ROUTE_PTH",)
    assert readiness.omitted == ()

    path, report = export_kicad_with_report(
        board,
        tmp_path / "plated-route.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert 'footprint "PHOTONX:RecoveredPlatedRoute"' in text
    assert 'pad "1" thru_hole oval' in text
    assert "(size 6.000000 2.000000)" in text
    assert "(drill oval 5.000000 1.000000)" in text
    assert '(layers "F.Cu" "B.Cu" "*.Mask")' in text
    assert '(net 1 "SIG")' in text
    assert report.exported_route_ids == ["ROUTE_PTH"]
    assert report.skipped_route_ids == []

    parsed = read_kicad_board_text(text)
    assert parsed["mechanical_slots"] == []

    audit = validate_kicad_connectivity_roundtrip(board, path, report)
    assert audit["routes"]["equal"]
    assert audit["roundtrip_equal"]
    assert audit["source_connectivity_complete"]
    assert audit["source_equivalent"]

    manifest = omission_manifest(report)
    assert manifest["exported_routes"] == ["ROUTE_PTH"]
    assert manifest["omitted_routes"] == []
    assert validate_omission_manifest(manifest) == []

    route_manifest = route_omission_manifest(board)
    assert route_manifest["exported_routes"] == ["ROUTE_PTH"]
    assert route_manifest["omitted_routes"] == []


def test_plated_route_without_resolved_exported_net_fails_closed(tmp_path):
    board, route = _proven_board(net_a=None, net_b=None, include_net=False)

    readiness = assess_route_export_readiness(board.routes, board)
    assert readiness.exportable == ()
    assert readiness.omitted == ("ROUTE_PTH",)
    assert readiness.reasons["ROUTE_PTH"] == "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"

    path, report = export_kicad_with_report(
        board,
        tmp_path / "plated-route-no-net.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert "RecoveredPlatedRoute" not in text
    assert report.exported_route_ids == []
    assert report.skipped_route_ids == ["ROUTE_PTH"]
    assert any(
        issue.code == "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"
        and issue.object_id == "ROUTE_PTH"
        for issue in report.issues
    )

    manifest = omission_manifest(report)
    assert manifest["omitted_routes"] == ["ROUTE_PTH"]
    assert validate_omission_manifest(manifest) == []

    audit = validate_kicad_connectivity_roundtrip(board, path, report)
    assert audit["routes"]["equal"]
    assert audit["roundtrip_equal"]
    assert not audit["source_connectivity_complete"]
    assert audit["losses"]["omitted_route_ids"] == ["ROUTE_PTH"]


def test_plated_route_with_conflicting_pad_nets_fails_closed():
    board, route = _proven_board(net_a="N1", net_b="N2")
    board.nets.append(NetGroup("N2", ["B"], 0.99, "ALT"))

    readiness = assess_route_export_readiness(board.routes, board)
    assert readiness.exportable == ()
    assert readiness.omitted == ("ROUTE_PTH",)
    assert readiness.reasons["ROUTE_PTH"] == "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"


def test_plated_route_requires_board_evidence_context():
    board, route = _proven_board()
    readiness = assess_route_export_readiness([route])
    assert readiness.exportable == ()
    assert readiness.omitted == ("ROUTE_PTH",)
    assert readiness.reasons["ROUTE_PTH"] == "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"

def test_plated_route_rejects_undeclared_inner_copper_layer():
    route = RoutedPath(
        "ROUTE_BAD_LAYER",
        ((0.0, 0.0), (4.0, 0.0)),
        1.0,
        plated="plated",
    )
    board = BoardModel(
        pads=[
            PadCandidate(
                "F",
                Point(2.0, 0.0),
                6.0,
                2.0,
                "O",
                "F.Cu",
                net_id="N1",
            ),
            PadCandidate(
                "X",
                Point(2.0, 0.0),
                6.0,
                2.0,
                "O",
                "In31.Cu",
                net_id="N1",
            ),
        ],
        routes=[route],
        nets=[NetGroup("N1", ["F", "X"], 0.99, "SIG")],
    )

    readiness = assess_route_export_readiness(board.routes, board)

    assert readiness.exportable == ()
    assert readiness.omitted == ("ROUTE_BAD_LAYER",)
    assert (
        readiness.reasons["ROUTE_BAD_LAYER"]
        == "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"
    )



def _x2_route_board(route, layers):
    pads = [
        PadCandidate(
            f"P{index}",
            Point(2.0, 0.0),
            6.0,
            2.0,
            "O",
            layer,
            net_id="N1",
        )
        for index, layer in enumerate(layers)
    ]
    return BoardModel(
        pads=pads,
        routes=[route],
        nets=[NetGroup("N1", [pad.id for pad in pads], 0.99, "SIG")],
        metadata={
            "x2_copper_stackup": {
                "status": "declared",
                "layers": ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"],
                "declared_copper_count": 4,
            }
        },
    )


def test_x2_buried_plated_route_is_not_widened_to_through_hole(tmp_path):
    route = RoutedPath(
        "ROUTE_BURIED",
        ((0.0, 0.0), (4.0, 0.0)),
        1.0,
        plated="plated",
        layer_span=("In1.Cu", "In2.Cu"),
        span_proven=True,
        x2_layer_span=(2, 3),
        x2_span_kind="buried",
    )
    board = _x2_route_board(route, ["In1.Cu", "In2.Cu"])

    readiness = assess_route_export_readiness(board.routes, board)
    assert readiness.exportable == ()
    assert readiness.omitted == ("ROUTE_BURIED",)
    assert (
        readiness.reasons["ROUTE_BURIED"]
        == "KICAD_PLATED_ROUTE_PARTIAL_SPAN_UNSUPPORTED"
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "buried-route.kicad_pcb",
    )
    assert "RecoveredPlatedRoute" not in path.read_text(encoding="utf-8")
    manifest = omission_manifest(report)
    assert manifest["omitted_routes"] == ["ROUTE_BURIED"]
    assert validate_omission_manifest(manifest) == []


def test_unresolved_x2_plated_route_span_fails_closed():
    route = RoutedPath(
        "ROUTE_UNRESOLVED",
        ((0.0, 0.0), (4.0, 0.0)),
        1.0,
        plated="plated",
        span_proven=False,
        x2_layer_span=(2, 3),
        x2_span_kind="buried",
    )
    board = _x2_route_board(route, ["In1.Cu", "In2.Cu"])

    readiness = assess_route_export_readiness(board.routes, board)
    assert readiness.exportable == ()
    assert (
        readiness.reasons["ROUTE_UNRESOLVED"]
        == "KICAD_PLATED_ROUTE_SPAN_UNPROVEN"
    )


def test_full_stack_route_rejects_blind_buried_kind_conflict():
    route = RoutedPath(
        "ROUTE_KIND_CONFLICT",
        ((0.0, 0.0), (4.0, 0.0)),
        1.0,
        plated="plated",
        layer_span=("F.Cu", "B.Cu"),
        span_proven=True,
        x2_layer_span=(1, 4),
        x2_span_kind="buried",
    )
    board = _x2_route_board(
        route,
        ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"],
    )

    readiness = assess_route_export_readiness(board.routes, board)
    assert readiness.exportable == ()
    assert (
        readiness.reasons["ROUTE_KIND_CONFLICT"]
        == "KICAD_PLATED_ROUTE_X2_KIND_MISMATCH"
    )
