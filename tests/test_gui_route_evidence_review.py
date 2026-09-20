from photonx_eda_pcb.excellon_routing import RoutedPath
from photonx_eda_pcb.gui.route_review import build_route_evidence_rows
from photonx_eda_pcb.models import BoardModel, NetGroup, PadCandidate, Point


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


def _proven_plated_board():
    route = RoutedPath(
        "R1",
        ((0.0, 0.0), (4.0, 0.0)),
        1.0,
        plated="plated",
    )
    return BoardModel(
        pads=[_pad("F", "F.Cu"), _pad("B", "B.Cu")],
        routes=[route],
        nets=[NetGroup("N1", ["F", "B"], 1.0, "SIG")],
    )


def test_route_evidence_marks_source_proven_plated_route_exportable():
    row = build_route_evidence_rows(_proven_plated_board())[0]

    assert row["status"] == "exportable"
    assert row["route_id"] == "R1"
    assert row["plating"] == "plated"
    assert row["net_id"] == "N1"
    assert row["net"] == "N1 (SIG)"
    assert row["export_kind"] == "plated"
    assert row["export_code"] is None
    assert row["segments"] == 1


def test_route_evidence_surfaces_unproven_x2_span_without_guessing():
    route = RoutedPath(
        "R_X2",
        ((0.0, 0.0), (4.0, 0.0)),
        1.0,
        plated="plated",
        span_proven=False,
        x2_layer_span=(2, 3),
        x2_span_kind="buried",
    )
    row = build_route_evidence_rows(BoardModel(routes=[route]))[0]

    assert row["status"] == "omitted"
    assert row["span"] == "X2 2 -> 3"
    assert row["x2_kind"] == "buried"
    assert row["export_code"] == "KICAD_PLATED_ROUTE_SPAN_UNPROVEN"
    assert "not source-proven" in row["reason"]


def test_route_evidence_keeps_exact_npth_route_exportable():
    route = RoutedPath(
        "R_NPTH",
        ((1.0, 2.0), (4.0, 2.0)),
        0.8,
        plated="non-plated",
    )
    row = build_route_evidence_rows(BoardModel(routes=[route]))[0]

    assert row["status"] == "exportable"
    assert row["export_kind"] == "npth"
    assert row["net_id"] is None
    assert row["net"] == "—"


def test_route_evidence_fails_closed_on_duplicate_route_identity():
    first = RoutedPath(
        "R_DUP",
        ((0.0, 0.0), (2.0, 0.0)),
        0.5,
        plated="non-plated",
    )
    second = RoutedPath(
        "R_DUP",
        ((0.0, 1.0), (2.0, 1.0)),
        0.5,
        plated="non-plated",
    )

    rows = build_route_evidence_rows(BoardModel(routes=[first, second]))

    assert [row["status"] for row in rows] == ["invalid", "invalid"]
    assert all(
        row["export_code"] == "KICAD_OBJECT_ID_DUPLICATE" for row in rows
    )


def test_route_evidence_surfaces_arbitrary_route_omission():
    route = RoutedPath(
        "R_MULTI",
        ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0)),
        0.5,
        plated="non-plated",
    )
    row = build_route_evidence_rows(BoardModel(routes=[route]))[0]

    assert row["status"] == "omitted"
    assert row["segments"] == 2
    assert row["export_code"] == "KICAD_ARBITRARY_ROUTE_UNSUPPORTED"
