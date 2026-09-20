from photonx_eda_pcb.excellon_routing.model import RoutedPath
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
from photonx_eda_pcb.mechanical_features.model import SlotFeature
from photonx_eda_pcb.models import BoardModel, DrillHit, NetGroup, PadCandidate, Point


def _assert_manifest_valid(report):
    assert validate_omission_manifest(omission_manifest(report)) == []


def test_backdrill_point_drill_is_not_widened_to_through_npth(tmp_path):
    board = BoardModel(
        drills=[
            DrillHit(
                "BD1",
                Point(1.0, 2.0),
                0.8,
                "non-plated",
                x2_aperture_function="backdrill",
            )
        ]
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "backdrill-point.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert "PHOTONX:RecoveredNPTHDrill" not in text
    assert report.exported_drill_ids == []
    assert report.skipped_drill_ids == ["BD1"]
    assert any(
        issue.code == "KICAD_DRILL_BACKDRILL_UNSUPPORTED"
        and issue.object_id == "BD1"
        for issue in report.issues
    )
    _assert_manifest_valid(report)


def test_backdrill_g85_slot_is_not_widened_to_through_npth(tmp_path):
    board = BoardModel(
        slots=[
            SlotFeature(
                "BDS1",
                (0.0, 0.0),
                (2.0, 0.0),
                0.8,
                "non-plated",
                "T01",
                x2_aperture_function="backdrill",
            )
        ]
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "backdrill-slot.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert "PHOTONX:RecoveredNPTHSlot" not in text
    assert report.exported_slot_ids == []
    assert report.skipped_slot_ids == ["BDS1"]
    assert any(
        issue.code == "KICAD_SLOT_BACKDRILL_UNSUPPORTED"
        and issue.object_id == "BDS1"
        for issue in report.issues
    )
    _assert_manifest_valid(report)


def test_backdrill_routed_path_is_not_widened_to_through_npth(tmp_path):
    board = BoardModel(
        routes=[
            RoutedPath(
                "BDR1",
                ((0.0, 0.0), (2.0, 0.0)),
                0.8,
                "non-plated",
                "T01",
                x2_aperture_function="backdrill",
            )
        ]
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "backdrill-route.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert "PHOTONX:RecoveredNPTHRoute" not in text
    assert report.exported_route_ids == []
    assert report.skipped_route_ids == ["BDR1"]
    assert any(
        issue.code == "KICAD_BACKDRILL_UNSUPPORTED"
        and issue.object_id == "BDR1"
        for issue in report.issues
    )
    _assert_manifest_valid(report)


def test_backdrill_cannot_escape_through_proven_via_path(tmp_path):
    board = BoardModel(
        nets=[NetGroup("N1", [], 1.0, "GND")],
        pads=[
            PadCandidate("PF", Point(0, 0), 1.0, 1.0, "C", "F.Cu", None, "N1"),
            PadCandidate("PB", Point(0, 0), 1.0, 1.0, "C", "B.Cu", None, "N1"),
        ],
        drills=[
            DrillHit(
                "BDV1",
                Point(0, 0),
                0.4,
                "plated",
                x2_aperture_function="backdrill",
            )
        ],
        metadata={
            "via_spans": [
                {
                    "drill_id": "BDV1",
                    "from_layer": "F.Cu",
                    "to_layer": "B.Cu",
                    "proven": True,
                    "pad_ids": ["PF", "PB"],
                }
            ]
        },
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "backdrill-via.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert "(via" not in text
    assert report.exported_via_span_ids == []
    assert report.skipped_via_span_ids == ["BDV1"]
    assert any(
        issue.code == "KICAD_PROVEN_VIA_BACKDRILL_UNSUPPORTED"
        and issue.object_id == "BDV1"
        for issue in report.issues
    )
    _assert_manifest_valid(report)
