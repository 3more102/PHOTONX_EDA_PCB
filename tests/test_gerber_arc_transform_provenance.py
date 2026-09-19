from pathlib import Path

import pytest

from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


def _write(tmp_path: Path, name: str, transform: str, arc: str) -> Path:
    path = tmp_path / name
    path.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        + transform
        + "%ADD10C,0.200*%\n"
        + "D10*\n"
        + "G75*\n"
        + "X010000Y000000D02*\n"
        + arc
        + "M02*\n",
        encoding="utf-8",
    )
    return path


def _arc_details(result) -> list[str]:
    return [
        evidence.detail
        for track in result.tracks
        for evidence in track.provenance.evidence
        if evidence.kind == "gerber_arc_tessellation"
    ]


def test_untransformed_ccw_arc_reports_ccw_source_and_output(tmp_path: Path):
    path = _write(
        tmp_path,
        "plain_ccw.gtl",
        "",
        "G03X000000Y010000I-010000J000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks
    assert all("direction=CCW" in detail for detail in _arc_details(result))
    assert all("source_direction=CCW" in detail for detail in _arc_details(result))
    assert all("output_direction=CCW" in detail for detail in _arc_details(result))


def test_single_axis_mirror_flips_ccw_arc_to_cw_output(tmp_path: Path):
    path = _write(
        tmp_path,
        "mirror_x_ccw.gtl",
        "%MIA1*%\n",
        "G03X000000Y010000I-010000J000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks
    assert all("source_direction=CCW" in detail for detail in _arc_details(result))
    assert all("output_direction=CW" in detail for detail in _arc_details(result))
    assert all("direction=CW" in detail for detail in _arc_details(result))


def test_two_axis_mirror_preserves_ccw_orientation(tmp_path: Path):
    path = _write(
        tmp_path,
        "mirror_xy_ccw.gtl",
        "%MIA1B1*%\n",
        "G03X000000Y010000I-010000J000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks
    assert all("source_direction=CCW" in detail for detail in _arc_details(result))
    assert all("output_direction=CCW" in detail for detail in _arc_details(result))


def test_single_axis_mirror_flips_cw_arc_to_ccw_output(tmp_path: Path):
    path = _write(
        tmp_path,
        "mirror_y_cw.gtl",
        "%MIB1*%\n",
        "G02X000000Y-010000I-010000J000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks
    assert all("source_direction=CW" in detail for detail in _arc_details(result))
    assert all("output_direction=CCW" in detail for detail in _arc_details(result))


def test_ir_and_uniform_sf_preserve_post_mirror_orientation(tmp_path: Path):
    path = _write(
        tmp_path,
        "mirror_scale_rotate_ccw.gtl",
        "%MIA1*%\n%SFA2B2*%\n%IR90*%\n",
        "G03X000000Y010000I-010000J000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks
    assert (result.tracks[0].start.x, result.tracks[0].start.y) == pytest.approx(
        (0.0, -2.0)
    )
    assert all("source_direction=CCW" in detail for detail in _arc_details(result))
    assert all("output_direction=CW" in detail for detail in _arc_details(result))
