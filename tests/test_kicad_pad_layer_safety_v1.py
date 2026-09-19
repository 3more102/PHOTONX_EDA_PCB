from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
from photonx_eda_pcb.models import BoardModel, PadCandidate, Point


def _pad(layer: str, *, pad_id: str = "P1", net_id=None, drill=None):
    return PadCandidate(
        pad_id,
        Point(1.0, 2.0),
        2.0,
        1.0,
        "R",
        layer,
        drill=drill,
        net_id=net_id,
    )


def test_noncanonical_inner_pad_layer_is_omitted_and_accounted(tmp_path):
    board = BoardModel(pads=[_pad("In31.Cu")])

    path, report = export_kicad_with_report(
        board,
        tmp_path / "invalid-pad-layer.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert '"In31.Cu" signal' not in text
    assert '(footprint "PHOTONX:RecoveredPad"' not in text
    assert '(layers "In31.Cu")' not in text
    assert report.exported_pads == 0
    assert report.skipped_pads == 1
    assert report.skipped_pad_ids == ["P1"]
    assert any(
        issue.code == "KICAD_PAD_LAYER_UNSUPPORTED"
        and issue.object_id == "P1"
        for issue in report.issues
    )

    manifest = omission_manifest(report)
    assert manifest["exported_pads"] == []
    assert manifest["skipped_pads"] == ["P1"]
    assert validate_omission_manifest(manifest) == []


def test_arbitrary_non_copper_pad_layer_is_omitted(tmp_path):
    board = BoardModel(pads=[_pad("Dwgs.User")])

    path, report = export_kicad_with_report(
        board,
        tmp_path / "user-layer-pad.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert '(layer "Dwgs.User")' not in text
    assert '(footprint "PHOTONX:RecoveredPad"' not in text
    assert report.skipped_pad_ids == ["P1"]
    assert any(
        issue.code == "KICAD_PAD_LAYER_UNSUPPORTED"
        for issue in report.issues
    )


def test_canonical_inner_smd_pad_still_exports_without_surface_evidence(tmp_path):
    board = BoardModel(pads=[_pad("In2.Cu")])

    path, report = export_kicad_with_report(
        board,
        tmp_path / "inner-pad.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert '    (1 "In1.Cu" signal)' in text
    assert '    (2 "In2.Cu" signal)' in text
    assert '(footprint "PHOTONX:RecoveredPad" (layer "In2.Cu")' in text
    assert '(layers "In2.Cu")' in text
    assert '"F.Paste"' not in text
    assert '"F.Mask"' not in text
    assert '"B.Paste"' not in text
    assert '"B.Mask"' not in text
    assert report.exported_pads == 1
    assert report.exported_pad_ids == ["P1"]
    assert report.skipped_pads == 0
    assert any(
        issue.code == "KICAD_SMD_NON_SURFACE_LAYER"
        and issue.object_id == "P1"
        for issue in report.issues
    )


def test_invalid_through_hole_pad_source_layer_is_not_relabelled(tmp_path):
    board = BoardModel(pads=[_pad("In31.Cu", drill=0.5)])

    path, report = export_kicad_with_report(
        board,
        tmp_path / "invalid-thru-pad-layer.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert '(footprint "PHOTONX:RecoveredPad"' not in text
    assert report.skipped_pad_ids == ["P1"]
    assert any(
        issue.code == "KICAD_PAD_LAYER_UNSUPPORTED"
        for issue in report.issues
    )


def test_bad_pad_layer_and_unresolved_net_report_both_but_skip_once(tmp_path):
    board = BoardModel(pads=[_pad("In31.Cu", net_id="MISSING")])

    _, report = export_kicad_with_report(
        board,
        tmp_path / "two-reasons-one-pad-skip.kicad_pcb",
    )

    assert report.exported_pads == 0
    assert report.skipped_pads == 1
    assert report.skipped_pad_ids == ["P1"]
    codes = {
        issue.code
        for issue in report.issues
        if issue.object_id == "P1"
    }
    assert "KICAD_PAD_LAYER_UNSUPPORTED" in codes
    assert "KICAD_NET_REFERENCE_UNRESOLVED" in codes
    assert validate_omission_manifest(omission_manifest(report)) == []
