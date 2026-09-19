from pathlib import Path
import pytest
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.errors import ParseError
FIX=Path(__file__).parent/"fixtures"/"led"

def test_excellon_extracts_six_drill_hits():
    result=ExcellonParser().parse(FIX/"drill.drl"); assert len(result.drills)==6; assert {d.tool for d in result.drills}=={"T01"}; assert all(d.plating=="unknown" for d in result.drills)


def test_excellon_honors_file_format_hint_before_metric_units(tmp_path):
    path=tmp_path/"format_before_units.drl"
    path.write_text(
        "M48\n"
        ";FILE_FORMAT=2:4\n"
        "METRIC,TZ\n"
        "T01C0.800\n"
        "%\n"
        "T01\n"
        "X123Y45\n"
        "M30\n",
        encoding="utf-8",
    )
    result=ExcellonParser().parse(path)
    assert len(result.drills)==1
    assert result.drills[0].center.x == pytest.approx(12.3)
    assert result.drills[0].center.y == pytest.approx(45.0)


def test_excellon_honors_file_format_hint_after_units(tmp_path):
    path=tmp_path/"format_after_units.drl"
    path.write_text(
        "M48\n"
        "METRIC,LZ\n"
        ";FILE_FORMAT=2:4\n"
        "T01C0.800\n"
        "%\n"
        "T01\n"
        "X123Y45\n"
        "M30\n",
        encoding="utf-8",
    )
    result=ExcellonParser().parse(path)
    assert len(result.drills)==1
    assert result.drills[0].center.x == pytest.approx(0.0123)
    assert result.drills[0].center.y == pytest.approx(0.0045)


def test_excellon_rejects_conflicting_file_format_hints(tmp_path):
    path=tmp_path/"conflicting_format.drl"
    path.write_text(
        "M48\n"
        ";FILE_FORMAT=2:4\n"
        ";FILE_FORMAT=3:3\n"
        "METRIC,LZ\n",
        encoding="utf-8",
    )
    with pytest.raises(ParseError, match="conflicting ;FILE_FORMAT"):
        ExcellonParser().parse(path)


def test_excellon_permissive_malformed_file_format_fails_closed(tmp_path):
    path=tmp_path/"malformed_format.drl"
    path.write_text(
        "M48\n"
        ";FILE_FORMAT=2:40\n"
        "METRIC,LZ\n"
        "T01C0.800\n"
        "%\n"
        "T01\n"
        "X123456Y001234\n"
        "M30\n",
        encoding="utf-8",
    )
    result=ExcellonParser(strict=False).parse(path)
    assert result.drills == []
    assert [d.code for d in result.diagnostics] == ["INVALID_EXCELLON_FILE_FORMAT"]


def test_excellon_rejects_file_format_after_coordinate_data(tmp_path):
    path=tmp_path/"late_format.drl"
    path.write_text(
        "M48\n"
        "METRIC,LZ\n"
        "T01C0.800\n"
        "%\n"
        "T01\n"
        "X001000Y001000\n"
        ";FILE_FORMAT=2:4\n"
        "M30\n",
        encoding="utf-8",
    )
    with pytest.raises(ParseError, match="must precede coordinate-bearing"):
        ExcellonParser().parse(path)


def test_excellon_accepts_feed_speed_before_tool_diameter(tmp_path):
    path=tmp_path/"altium_tool_order.drl"
    path.write_text(
        "M48\n"
        ";FILE_FORMAT=2:4\n"
        "INCH,TZ\n"
        ";TYPE=PLATED\n"
        "T1F00S00C0.0118\n"
        "%\n"
        "T1\n"
        "X001000Y001000\n"
        "M30\n",
        encoding="utf-8",
    )
    result=ExcellonParser().parse(path)
    assert len(result.drills)==1
    assert result.drills[0].diameter == pytest.approx(0.0118 * 25.4)
    assert result.drills[0].plating == "unknown"


def test_excellon_keeps_existing_diameter_before_feed_speed_form(tmp_path):
    path=tmp_path/"classic_tool_order.drl"
    path.write_text(
        "M48\n"
        "METRIC,LZ\n"
        "T1C0.800F00S00\n"
        "%\n"
        "T1\n"
        "X001000Y001000\n"
        "M30\n",
        encoding="utf-8",
    )
    result=ExcellonParser().parse(path)
    assert len(result.drills)==1
    assert result.drills[0].diameter == pytest.approx(0.8)
