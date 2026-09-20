from pathlib import Path

import pytest

from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.pipeline import reconstruct
from photonx_eda_pcb.roundtrip.kicad_connectivity import compare_kicad_connectivity


GERBER_BODY = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.000*%
D10*
X010000Y010000D03*
M02*
"""


def _gerber(file_function: str) -> str:
    return f"%TF.FileFunction,{file_function}*%\n" + GERBER_BODY


def _drill(file_function: str) -> str:
    return (
        "M48\n"
        f"; #@! TF.FileFunction,{file_function}\n"
        "METRIC\n"
        "T01C0.400\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n"
    )


def _write_four_layer_board(tmp_path: Path, drill_function: str) -> None:
    (tmp_path / "top.gbr").write_text(
        _gerber("Copper,L1,Top,Signal"),
        encoding="utf-8",
    )
    (tmp_path / "inner1.gbr").write_text(
        _gerber("Copper,L2,Inr,Signal"),
        encoding="utf-8",
    )
    (tmp_path / "inner2.gbr").write_text(
        _gerber("Copper,L3,Inr,Signal"),
        encoding="utf-8",
    )
    (tmp_path / "bottom.gbr").write_text(
        _gerber("Copper,L4,Bot,Signal"),
        encoding="utf-8",
    )
    (tmp_path / "span.drl").write_text(
        _drill(drill_function),
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    ("file_function", "expected_layers"),
    [
        ("Plated,1,2,Blind,Drill", ("F.Cu", "In1.Cu")),
        ("Plated,2,3,Buried,Drill", ("In1.Cu", "In2.Cu")),
    ],
)
def test_x2_blind_and_buried_spans_export_as_exact_kicad_blind_vias(
    tmp_path: Path,
    file_function: str,
    expected_layers: tuple[str, str],
):
    _write_four_layer_board(tmp_path, file_function)

    board = reconstruct(tmp_path).board
    out_path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    text = out_path.read_text(encoding="utf-8")
    readback = read_kicad_board_text(text)
    audit = compare_kicad_connectivity(board, readback, report)

    assert len(readback["vias"]) == 1
    via = readback["vias"][0]
    assert via["type"] == "blind"
    assert via["layers"] == expected_layers
    assert via["locked"] is False
    assert "(via blind " in text
    assert "(via micro " not in text

    assert len(report.exported_via_span_ids) == 1
    assert report.skipped_via_span_ids == []
    expected_support = set(board.metadata["via_spans"][0]["pad_ids"])
    assert set(report.represented_via_pad_ids) == expected_support
    assert report.skipped_pad_ids == []
    assert set(audit["represented_via_pad_ids"]) == expected_support
    assert audit["vias"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_equivalent"] is True


def test_x2_blind_kind_conflicting_with_full_stack_span_fails_closed(
    tmp_path: Path,
):
    _write_four_layer_board(
        tmp_path,
        "Plated,1,4,Blind,Drill",
    )

    board = reconstruct(tmp_path).board
    out_path, report = export_kicad_with_report(
        board,
        tmp_path / "board.kicad_pcb",
    )
    readback = read_kicad_board_text(
        out_path.read_text(encoding="utf-8")
    )

    assert readback["vias"] == []
    assert report.exported_via_span_ids == []
    assert len(report.skipped_via_span_ids) == 1
    assert any(
        issue.code == "KICAD_PROVEN_VIA_TYPE_UNPROVEN"
        for issue in report.issues
    )
    assert validate_omission_manifest(omission_manifest(report)) == []
