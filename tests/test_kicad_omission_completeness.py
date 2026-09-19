from photonx_eda_pcb.excellon_routing import RoutedPath
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest,write_omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
from photonx_eda_pcb.models import BoardModel,CopperRegion,Point
import json


def test_kicad_report_and_manifest_cover_all_omitted_geometry(tmp_path):
    region=CopperRegion(
        "region-1",
        (Point(0,0),Point(2,0),Point(2,2),Point(0,2)),
        "F.Cu",
    )
    route=RoutedPath("route-1",((0,0),(2,0),(2,2)),.5)
    board=BoardModel(regions=[region],routes=[route])

    _,report=export_kicad_with_report(board,tmp_path/"board.kicad_pcb")

    assert report.skipped_regions==1
    assert report.skipped_region_ids==["region-1"]
    assert report.skipped_routes==1
    assert report.skipped_route_ids==["route-1"]
    assert {
        (issue.code,issue.object_id)
        for issue in report.issues
    } >= {
        ("KICAD_COPPER_REGION_UNSUPPORTED","region-1"),
        ("KICAD_ARBITRARY_ROUTE_UNSUPPORTED","route-1"),
    }

    data=omission_manifest(report)
    assert data["skipped_regions"]==["region-1"]
    assert data["omitted_routes"]==["route-1"]
    assert validate_omission_manifest(data)==[]

    path=write_omission_manifest(report,tmp_path/"omissions.json")
    saved=json.loads(path.read_text())
    assert saved["skipped_regions"]==["region-1"]
    assert saved["omitted_routes"]==["route-1"]


def test_omission_validation_requires_reasons_for_regions_and_routes():
    data={
        "exported_slots":[],
        "skipped_slots":[],
        "skipped_regions":["region-1"],
        "omitted_routes":["route-1"],
        "issues":[],
    }
    assert validate_omission_manifest(data)==[
        "OMISSION_REGION_WITHOUT_REASON",
        "OMISSION_ROUTE_WITHOUT_REASON",
    ]


def test_omission_validation_rejects_duplicate_omission_ids():
    data={
        "exported_slots":[],
        "skipped_slots":[],
        "skipped_regions":["region-1","region-1"],
        "omitted_routes":["route-1","route-1"],
        "issues":[
            {"object_id":"region-1"},
            {"object_id":"route-1"},
        ],
    }
    assert validate_omission_manifest(data)==[
        "OMISSION_REGION_DUPLICATE_ID",
        "OMISSION_ROUTE_DUPLICATE_ID",
    ]


def test_omission_validation_rejects_wrong_region_and_route_reason_codes():
    data={
        "exported_slots":[],
        "skipped_slots":[],
        "skipped_regions":["region-1"],
        "omitted_routes":["route-1"],
        "issues":[
            {"object_id":"region-1","code":"SOME_OTHER_REASON"},
            {"object_id":"route-1","code":"SOME_OTHER_REASON"},
        ],
    }
    assert validate_omission_manifest(data)==[
        "OMISSION_REGION_WITHOUT_REASON",
        "OMISSION_ROUTE_WITHOUT_REASON",
    ]
