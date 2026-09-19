from photonx_eda_pcb.models import BoardModel, NetGroup, PadCandidate, Point
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report


def test_kicad_export_escapes_line_breaks_and_special_characters(tmp_path):
    label = 'VCC "A"\\sense\naux\rret'
    pad_id = 'P"1\\top\nref'
    board = BoardModel(
        nets=[NetGroup("N1", [], 1.0, label=label)],
        pads=[PadCandidate(pad_id, Point(1, 2), 2, 2, "C", "F.Cu", net_id="N1")],
    )

    path, report = export_kicad_with_report(board, tmp_path / "escaped.kicad_pcb")
    text = path.read_text(encoding="utf-8")

    assert '  (net 1 "VCC \\"A\\"\\\\sense\\naux\\rret")' in text
    assert '(property "Reference" "P\\"1\\\\top\\nref"' in text
    assert label not in text
    assert pad_id not in text
    assert "\r" not in text
    assert report.ok
