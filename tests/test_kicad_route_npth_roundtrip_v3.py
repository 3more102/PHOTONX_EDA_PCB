from photonx_eda_pcb.excellon_routing import (
    RoutedPath,
    assess_route_export_readiness,
)
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
from photonx_eda_pcb.exporters.route_omissions import (
    route_omission_manifest,
    validate_route_omission_manifest,
)
from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.roundtrip import validate_kicad_connectivity_roundtrip


def test_exact_straight_non_plated_route_exports_and_roundtrips(tmp_path):
    route = RoutedPath(
        "ROUTE_NPTH",
        ((1.0, 2.0), (4.0, 6.0)),
        0.8,
        plated="non-plated",
    )
    board = BoardModel(routes=[route])

    path, report = export_kicad_with_report(
        board,
        tmp_path / "route.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert 'footprint "PHOTONX:RecoveredNPTHRoute"' in text
    assert "(at 2.500000 4.000000)" in text
    assert "(at 0 0 53.130102)" in text
    assert "(size 5.800000 0.800000)" in text
    assert "(drill oval 5.800000 0.800000)" in text
    assert report.exported_routes == 1
    assert report.exported_route_ids == ["ROUTE_NPTH"]
    assert report.skipped_routes == 0
    assert report.skipped_route_ids == []

    audit = validate_kicad_connectivity_roundtrip(board, path, report)
    assert audit["routes"]["equal"]
    assert audit["roundtrip_equal"]
    assert audit["source_connectivity_complete"]
    assert audit["source_equivalent"]


def test_non_exact_route_remains_explicit_source_loss(tmp_path):
    route = RoutedPath(
        "ROUTE_PLATED",
        ((0.0, 0.0), (2.0, 0.0)),
        0.5,
        plated="plated",
    )
    board = BoardModel(routes=[route])

    path, report = export_kicad_with_report(
        board,
        tmp_path / "route.kicad_pcb",
    )

    assert report.exported_route_ids == []
    assert report.skipped_route_ids == ["ROUTE_PLATED"]

    audit = validate_kicad_connectivity_roundtrip(board, path, report)
    assert audit["routes"]["equal"]
    assert audit["roundtrip_equal"]
    assert not audit["source_connectivity_complete"]
    assert not audit["source_equivalent"]
    assert audit["losses"]["omitted_route_ids"] == ["ROUTE_PLATED"]


def test_route_geometry_drift_fails_roundtrip(tmp_path):
    route = RoutedPath(
        "ROUTE_NPTH",
        ((1.0, 2.0), (4.0, 6.0)),
        0.8,
        plated="non-plated",
    )
    board = BoardModel(routes=[route])
    path, report = export_kicad_with_report(
        board,
        tmp_path / "route.kicad_pcb",
    )

    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "(size 5.800000 0.800000)",
        "(size 5.900000 0.800000)",
        1,
    )
    path.write_text(text, encoding="utf-8")

    audit = validate_kicad_connectivity_roundtrip(board, path, report)
    assert not audit["routes"]["equal"]
    assert not audit["roundtrip_equal"]


def test_route_export_and_omission_manifests_are_partitioned():
    board = BoardModel(
        routes=[
            RoutedPath(
                "EXACT",
                ((0.0, 0.0), (2.0, 0.0)),
                0.5,
                plated="non-plated",
            ),
            RoutedPath(
                "SKIP",
                ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0)),
                0.5,
                plated="non-plated",
            ),
        ]
    )

    readiness = assess_route_export_readiness(board.routes)
    assert readiness.exportable == ("EXACT",)
    assert readiness.omitted == ("SKIP",)

    data = route_omission_manifest(board)
    assert data["exported_routes"] == ["EXACT"]
    assert data["omitted_routes"] == ["SKIP"]
    assert data["reasons"] == {
        "SKIP": "KICAD_ARBITRARY_ROUTE_UNSUPPORTED"
    }
    assert validate_route_omission_manifest(data) == []

    manifest = {
        "exported_routes": ["R", "R"],
        "omitted_routes": ["R"],
        "issues": [
            {
                "object_id": "R",
                "code": "KICAD_ARBITRARY_ROUTE_UNSUPPORTED",
            }
        ],
    }
    assert validate_omission_manifest(manifest) == [
        "OMISSION_EXPORTED_ROUTE_DUPLICATE_ID",
        "OMISSION_ROUTE_BOTH_EXPORTED_AND_SKIPPED",
    ]


def test_exact_route_is_not_counted_as_recovered_slot_geometry(tmp_path):
    board = BoardModel(
        routes=[
            RoutedPath(
                "ROUTE_ONLY",
                ((0.0, 0.0), (3.0, 0.0)),
                0.6,
                plated="non-plated",
            )
        ]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "route-only.kicad_pcb",
    )

    audit = validate_kicad_connectivity_roundtrip(board, path, report)
    assert audit["slot_geometry"]["equal"]
    assert audit["slot_geometry"]["expected_count"] == 0
    assert audit["slot_geometry"]["observed_count"] == 0
    assert audit["routes"]["equal"]
