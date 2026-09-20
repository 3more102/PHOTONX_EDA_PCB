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
