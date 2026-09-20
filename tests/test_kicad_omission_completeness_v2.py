import json

from photonx_eda_pcb.excellon_routing import RoutedPath
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import (
    omission_manifest,
    write_omission_manifest,
)
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.models import BoardModel, CopperRegion, DrillHit, PadCandidate, Point, Track


def _square(region_id: str, x0: float, *, holes=()) -> CopperRegion:
    return CopperRegion(
        region_id,
        (
            Point(x0, 0),
            Point(x0 + 2, 0),
            Point(x0 + 2, 2),
            Point(x0, 2),
            Point(x0, 0),
        ),
        "F.Cu",
        holes=holes,
    )


def test_report_and_manifest_cover_exported_and_omitted_geometry(tmp_path):
    hole = (
        Point(6.5, 0.5),
        Point(7.5, 0.5),
        Point(7.5, 1.5),
        Point(6.5, 1.5),
        Point(6.5, 0.5),
    )
    board = BoardModel(
        regions=[
            _square("R_OK", 0),
            _square("R_SKIP", 4, holes=(hole,)),
        ],
        tracks=[
            Track("T_OK", Point(0, 3), Point(1, 3), 0.2, "F.Cu"),
            Track("T_SKIP", Point(0, 4), Point(1, 4), 0.2, "F.Cu", net_id="MISSING"),
        ],
        slots=[
            SlotFeature("S_OK", (10, 0), (14, 0), 1.0, "non-plated"),
            SlotFeature("S_SKIP", (20, 0), (24, 0), 1.0, "unknown"),
        ],
        routes=[
            RoutedPath("ROUTE_SKIP", ((30, 0), (32, 0), (32, 2)), 0.5),
        ],
    )

    _, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    data = omission_manifest(report)

    assert data["exported_slots"] == ["S_OK"]
    assert data["skipped_slots"] == ["S_SKIP"]
    assert data["exported_regions"] == ["R_OK"]
    assert data["skipped_regions"] == ["R_SKIP"]
    assert data["exported_tracks"] == ["T_OK"]
    assert data["skipped_tracks"] == ["T_SKIP"]
    assert data["omitted_routes"] == ["ROUTE_SKIP"]
    assert validate_omission_manifest(data) == []

    path = write_omission_manifest(report, tmp_path / "omissions.json")
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved == data


def test_validator_rejects_duplicates_overlap_and_missing_reasons():
    data = {
        "exported_slots": ["S", "S"],
        "skipped_slots": ["S"],
        "exported_regions": ["R"],
        "skipped_regions": ["R"],
        "exported_tracks": ["T"],
        "skipped_tracks": ["T", "T"],
        "omitted_routes": ["Q", "Q"],
        "issues": [],
    }

    assert validate_omission_manifest(data) == [
        "OMISSION_EXPORTED_SLOT_DUPLICATE_ID",
        "OMISSION_SKIPPED_TRACK_DUPLICATE_ID",
        "OMISSION_ROUTE_DUPLICATE_ID",
        "OMISSION_SLOT_BOTH_EXPORTED_AND_SKIPPED",
        "OMISSION_REGION_BOTH_EXPORTED_AND_SKIPPED",
        "OMISSION_TRACK_BOTH_EXPORTED_AND_SKIPPED",
        "OMISSION_SKIPPED_SLOT_WITHOUT_REASON",
        "OMISSION_SKIPPED_REGION_WITHOUT_REASON",
        "OMISSION_SKIPPED_TRACK_WITHOUT_REASON",
        "OMISSION_ROUTE_WITHOUT_REASON",
    ]


def test_validator_requires_family_specific_reason_codes():
    data = {
        "skipped_slots": ["S"],
        "skipped_regions": ["R"],
        "skipped_tracks": ["T"],
        "omitted_routes": ["Q"],
        "issues": [
            {"object_id": "S", "code": "KICAD_COPPER_REGION_HOLES_UNSUPPORTED"},
            {"object_id": "R", "code": "KICAD_SLOT_PLATING_UNKNOWN"},
            {"object_id": "T", "code": "KICAD_ARBITRARY_ROUTE_UNSUPPORTED"},
            {"object_id": "Q", "code": "KICAD_NET_REFERENCE_UNRESOLVED"},
        ],
    }

    assert validate_omission_manifest(data) == [
        "OMISSION_SKIPPED_SLOT_WITHOUT_REASON",
        "OMISSION_SKIPPED_REGION_WITHOUT_REASON",
        "OMISSION_SKIPPED_TRACK_WITHOUT_REASON",
        "OMISSION_ROUTE_WITHOUT_REASON",
    ]


def test_legacy_slot_only_manifest_remains_valid():
    data = {
        "exported_slots": ["S_OK"],
        "skipped_slots": ["S_SKIP"],
        "issues": [
            {
                "object_id": "S_SKIP",
                "code": "KICAD_SLOT_PLATING_UNKNOWN",
            }
        ],
    }

    assert validate_omission_manifest(data) == []


def test_manifest_records_proven_via_span_connectivity_omission(tmp_path):
    board = BoardModel(
        pads=[
            PadCandidate("P_F", Point(0, 0), 1.0, 1.0, "C", "F.Cu"),
            PadCandidate("P_B", Point(0, 0), 1.0, 1.0, "C", "B.Cu"),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, "plated")],
        metadata={
            "via_spans": [
                {
                    "drill_id": "D1",
                    "from_layer": "F.Cu",
                    "to_layer": "B.Cu",
                    "confidence": 0.95,
                    "proven": True,
                    "pad_ids": ["P_B", "P_F"],
                    "evidence": [],
                }
            ]
        },
    )
    _, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    data = omission_manifest(report)
    assert data["omitted_via_spans"] == ["D1"]
    assert any(
        item["code"] == "KICAD_PROVEN_VIA_SPAN_UNSUPPORTED"
        and item["object_id"] == "D1"
        for item in data["issues"]
    )
    assert validate_omission_manifest(data) == []


def test_manifest_records_unsupported_pad_layer_omission(tmp_path):
    board = BoardModel(
        pads=[
            PadCandidate(
                "P_BAD_LAYER",
                Point(0, 0),
                1,
                1,
                "C",
                "In31.Cu",
            )
        ]
    )
    _, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    data = omission_manifest(report)

    assert data["exported_pads"] == []
    assert data["skipped_pads"] == ["P_BAD_LAYER"]
    assert any(
        item["code"] == "KICAD_PAD_LAYER_UNSUPPORTED"
        and item["object_id"] == "P_BAD_LAYER"
        for item in data["issues"]
    )
    assert validate_omission_manifest(data) == []
