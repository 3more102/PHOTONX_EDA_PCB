from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.models import BoardModel, PadCandidate, Point


def _export_pad(tmp_path, pad):
    path, report = export_kicad_with_report(
        BoardModel(pads=[pad]),
        tmp_path / "pad.kicad_pcb",
    )
    return path.read_text(encoding="utf-8"), report


def test_front_smd_pad_uses_front_surface_layers(tmp_path):
    text, report = _export_pad(
        tmp_path,
        PadCandidate("PF", Point(1, 2), 2, 1, "R", "F.Cu"),
    )

    assert '(layers "F.Cu" "F.Paste" "F.Mask")' in text
    assert '(layer "F.SilkS") hide' in text
    assert not report.issues


def test_back_smd_pad_uses_back_surface_layers(tmp_path):
    text, report = _export_pad(
        tmp_path,
        PadCandidate("PB", Point(1, 2), 2, 1, "R", "B.Cu"),
    )

    assert '(layers "B.Cu" "B.Paste" "B.Mask")' in text
    assert '(layer "B.SilkS") hide' in text
    assert '"F.Paste"' not in text
    assert '"F.Mask"' not in text
    assert not report.issues


def test_non_surface_smd_pad_does_not_invent_paste_or_mask(tmp_path):
    text, report = _export_pad(
        tmp_path,
        PadCandidate("PI", Point(1, 2), 2, 1, "R", "In1.Cu"),
    )

    assert '(layers "In1.Cu")' in text
    assert '"F.Paste"' not in text
    assert '"F.Mask"' not in text
    assert '"B.Paste"' not in text
    assert '"B.Mask"' not in text
    assert any(
        issue.code == "KICAD_SMD_NON_SURFACE_LAYER" and issue.object_id == "PI"
        for issue in report.issues
    )


def test_noncanonical_pad_layer_is_omitted_fail_closed(tmp_path):
    text, report = _export_pad(
        tmp_path,
        PadCandidate("PX", Point(1, 2), 2, 1, "R", "In31.Cu"),
    )

    assert "PHOTONX:RecoveredPad" not in text
    assert '"In31.Cu"' not in text
    assert report.exported_pads == 0
    assert report.skipped_pads == 1
    assert report.skipped_pad_ids == ["PX"]
    assert any(
        issue.code == "KICAD_PAD_LAYER_UNSUPPORTED"
        and issue.object_id == "PX"
        for issue in report.issues
    )
