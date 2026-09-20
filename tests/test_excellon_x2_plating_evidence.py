from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "board.drl"
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("file_function", "expected"),
    [
        ("Plated,1,2,PTH", "plated"),
        ("NonPlated,1,2,NPTH", "non-plated"),
    ],
)
def test_file_function_plating_is_applied_to_drill_hits(
    tmp_path: Path,
    file_function: str,
    expected: str,
):
    path = _write(
        tmp_path,
        "M48\n"
        f"; #@! TF.FileFunction,{file_function}\n"
        "METRIC\n"
        "T01C0.600\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.drills) == 1
    assert result.drills[0].plating == expected
    assert {
        evidence.kind for evidence in result.drills[0].provenance.evidence
    } == {"excellon_x2_file_plating"}


def test_mixed_file_uses_modal_tool_plating_and_td_clear(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "; #@! TF.FileFunction,MixedPlating,1,2,PTH\n"
        "METRIC\n"
        "; #@! TA.AperFunction,Plated,PTH,ViaDrill\n"
        "T01C0.400\n"
        "; #@! TD\n"
        "; #@! TA.AperFunction,NonPlated,NPTH,ComponentDrill\n"
        "T02C1.000\n"
        "; #@! TD\n"
        "T03C0.500\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "T02\n"
        "X2.000Y2.000\n"
        "T03\n"
        "X3.000Y3.000\n"
        "M30\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert [drill.plating for drill in result.drills] == [
        "plated",
        "non-plated",
        "unknown",
    ]
    assert result.drills[0].provenance.evidence[0].kind == "excellon_x2_tool_plating"
    assert result.drills[1].provenance.evidence[0].kind == "excellon_x2_tool_plating"
    assert result.drills[2].provenance.evidence == []


def test_file_function_plating_propagates_to_slots(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "; #@! TF.FileFunction,NonPlated,1,2,NPTH\n"
        "METRIC\n"
        "T01C1.000\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000G85X3.000Y1.000\n"
        "M30\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.slots) == 1
    assert result.slots[0].plated == "non-plated"
    assert any(
        evidence.kind == "excellon_x2_file_plating"
        for evidence in result.slots[0].provenance.evidence
    )


def test_conflicting_file_and_tool_plating_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "; #@! TF.FileFunction,Plated,1,2,PTH\n"
        "METRIC\n"
        "; #@! TA.AperFunction,NonPlated,NPTH,ComponentDrill\n"
        "T01C1.000\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    with pytest.raises(ParseError, match="file/tool plating conflict"):
        ExcellonParser(strict=True).parse(path)

    permissive = ExcellonParser(strict=False).parse(path)
    assert permissive.drills == []
    assert permissive.slots == []
    assert permissive.routes == []
    assert any(
        diagnostic.code == "INVALID_EXCELLON_X2_PLATING"
        for diagnostic in permissive.diagnostics
    )


def test_malformed_recognized_plating_attribute_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "; #@! TF.FileFunction,Plated,1,PTH\n"
        "METRIC\n"
        "T01C0.600\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    with pytest.raises(ParseError, match="malformed Excellon X2 FileFunction"):
        ExcellonParser(strict=True).parse(path)

    permissive = ExcellonParser(strict=False).parse(path)
    assert permissive.drills == []
    assert any(
        diagnostic.code == "INVALID_EXCELLON_X2_PLATING"
        for diagnostic in permissive.diagnostics
    )
