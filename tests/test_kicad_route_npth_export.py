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


def test_exact_straight_non_plated_route_exports_as_npth_slot(tmp_path):
    route=RoutedPath(
        "ROUTE_NPTH",
        ((1.0,2.0),(4.0,6.0)),
        0.8,
        plated="non-plated",
    )
    board=BoardModel(routes=[route])

    path,report=export_kicad_with_report(board,tmp_path/"route.kicad_pcb")
    text=path.read_text(encoding="utf-8")

    assert 'footprint "PHOTONX:RecoveredNPTHRoute"' in text
    assert "(at 2.500000 4.000000)" in text
    assert "(at 0 0 53.130102)" in text
    assert "(size 5.800000 0.800000)" in text
    assert "(drill oval 5.800000 0.800000)" in text
    assert report.exported_routes==1
    assert report.exported_route_ids==["ROUTE_NPTH"]
    assert report.skipped_routes==0
    assert report.skipped_route_ids==[]

    manifest=omission_manifest(report)
    assert manifest["exported_routes"]==["ROUTE_NPTH"]
    assert manifest["omitted_routes"]==[]
    assert validate_omission_manifest(manifest)==[]


def test_only_exact_non_plated_route_is_exportable():
    routes=[
        RoutedPath("EXACT",((0,0),(2,0)),0.5,plated="non_plated"),
        RoutedPath("UNKNOWN",((0,0),(2,0)),0.5),
        RoutedPath("PLATED",((0,0),(2,0)),0.5,plated="plated"),
        RoutedPath("POLYLINE",((0,0),(1,0),(1,1)),0.5,plated="non-plated"),
        RoutedPath("NONFINITE",((0,0),(float("nan"),1)),0.5,plated="non-plated"),
    ]

    readiness=assess_route_export_readiness(routes)

    assert readiness.exportable==("EXACT",)
    assert readiness.omitted==("NONFINITE","PLATED","POLYLINE","UNKNOWN")
    assert set(readiness.reasons)==set(readiness.omitted)
    assert all(
        readiness.reasons[route_id]=="KICAD_ARBITRARY_ROUTE_UNSUPPORTED"
        for route_id in readiness.omitted
    )


def test_route_manifest_tracks_exported_and_omitted_without_overlap():
    board=BoardModel(routes=[
        RoutedPath("EXACT",((0,0),(2,0)),0.5,plated="non-plated"),
        RoutedPath("SKIP",((0,0),(1,0),(1,1)),0.5,plated="non-plated"),
    ])

    data=route_omission_manifest(board)

    assert data["exported_routes"]==["EXACT"]
    assert data["omitted_routes"]==["SKIP"]
    assert data["reasons"]=={"SKIP":"KICAD_ARBITRARY_ROUTE_UNSUPPORTED"}
    assert validate_route_omission_manifest(data)==[]


def test_unified_manifest_rejects_route_export_omission_overlap():
    data={
        "exported_routes":["R","R"],
        "omitted_routes":["R"],
        "issues":[
            {
                "object_id":"R",
                "code":"KICAD_ARBITRARY_ROUTE_UNSUPPORTED",
            }
        ],
    }

    assert validate_omission_manifest(data)==[
        "OMISSION_EXPORTED_ROUTE_DUPLICATE_ID",
        "OMISSION_ROUTE_BOTH_EXPORTED_AND_SKIPPED",
    ]
