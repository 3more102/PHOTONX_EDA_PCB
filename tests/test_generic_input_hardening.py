from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.format_detection import detect_format
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.parsers.layer_map import infer_layer
from photonx_eda_pcb.parsers.manifest import discover_manufacturing_files
from photonx_eda_pcb.preflight import preflight


def test_gerber_modal_d01_reuses_operation(tmp_path: Path):
    p = tmp_path / "top.gtl"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "D02*\n"
        "X000000Y000000*\n"
        "D01*\n"
        "X010000Y000000*\n"
        "X010000Y010000*\n"
        "M02*\n",
        encoding="utf-8",
    )
    result = GerberRS274XParser("F.Cu").parse(p)
    assert len(result.tracks) == 2
    assert result.tracks[1].start.x == pytest.approx(1.0)
    assert result.tracks[1].end.y == pytest.approx(1.0)


def test_gerber_legacy_units_and_absolute_mode(tmp_path: Path):
    metric = tmp_path / "metric.gtl"
    metric.write_text(
        "%FSLAX24Y24*%\n"
        "G71*\n"
        "G90*\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "M02*\n",
        encoding="utf-8",
    )
    mr = GerberRS274XParser("F.Cu").parse(metric)
    assert mr.tracks[0].end.x == pytest.approx(1.0)

    inch = tmp_path / "inch.gtl"
    inch.write_text(
        "%FSLAX24Y24*%\n"
        "G70*\n"
        "%ADD10C,0.010*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "M02*\n",
        encoding="utf-8",
    )
    ir = GerberRS274XParser("F.Cu").parse(inch)
    assert ir.tracks[0].end.x == pytest.approx(25.4)


def test_gerber_incremental_mode_remains_fail_closed(tmp_path: Path):
    p = tmp_path / "bad.gtl"
    p.write_text("%FSLAX24Y24*%\nG91*\nM02*\n", encoding="utf-8")
    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu").parse(p)


def test_gerber_utf8_bom_is_accepted(tmp_path: Path):
    p = tmp_path / "bom.gtl"
    p.write_text(
        "\ufeff%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "M02*\n",
        encoding="utf-8",
    )
    assert len(GerberRS274XParser("F.Cu").parse(p).tracks) == 1


def test_excellon_m71_and_feed_speed_tool_definition(tmp_path: Path):
    p = tmp_path / "legacy.drd"
    p.write_text(
        "M48\n"
        "M71\n"
        "T01C0.800F120S300\n"
        "%\n"
        "T01\n"
        "X1.000Y2.000\n"
        "M30\n",
        encoding="utf-8",
    )
    result = ExcellonParser().parse(p)
    assert len(result.drills) == 1
    assert result.drills[0].diameter == pytest.approx(0.8)
    assert result.drills[0].center.y == pytest.approx(2.0)


def test_headerless_excellon_is_detected_but_units_are_not_guessed(tmp_path: Path):
    p = tmp_path / "mystery"
    p.write_text(
        "T01C0.800\n"
        "T01\n"
        "X1.000Y2.000\n"
        "M30\n",
        encoding="utf-8",
    )
    guess = detect_format(p.name, p.read_text())
    assert guess.format == "excellon"

    discovered = discover_manufacturing_files(tmp_path)
    assert len(discovered) == 1
    assert discovered[0].kind == "drill"

    report = preflight(tmp_path)
    assert not report.ready_for_strict_reconstruction
    assert any("EXCELLON_UNITS_UNDECLARED" in x for x in report.strict_blockers)


def test_common_legacy_layer_names_are_mapped():
    assert infer_layer("board.plc") == "F.SilkS"
    assert infer_layer("board.sts") == "B.Mask"
    assert infer_layer("board.dim") == "Edge.Cuts"
    assert infer_layer("board.g1") == "In1.Cu"
    assert infer_layer("board.gp2") == "In2.Cu"
