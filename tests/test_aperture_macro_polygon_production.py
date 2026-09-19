from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.geometry_kernel import region_shape
from photonx_eda_pcb.gerber_image import (
    polygonize_regular_polygon_flash,
    polygonize_regular_polygon_track,
)
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


HEADER = """%FSLAX24Y24*%
%MOMM*%
"""


def _write(tmp_path: Path, macro_body: str, body: str) -> Path:
    path = tmp_path / "macro_polygon.gtl"
    path.write_text(
        HEADER
        + f"%AMPOLY*{macro_body}*%\n"
        + "%ADD10POLY*%\n"
        + "D10*\n"
        + body
        + "M02*\n",
        encoding="utf-8",
    )
    return path


def test_code5_polygon_macro_flash_reduces_exactly_to_standard_polygon(tmp_path: Path):
    path = _write(tmp_path, "5,1,6,0,0,4,30", "X010000Y020000D03*\n")

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_regular_polygon_flash(
        1.0,
        2.0,
        4.0,
        6,
        base_rotation_deg=30.0,
    ).geometry

    assert result.pads == []
    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).symmetric_difference(
        expected
    ).area == pytest.approx(0.0, abs=1e-12)
    assert any(
        evidence.kind == "gerber_polygon_flash"
        and "vertices=6" in evidence.detail
        and "template_rotation_deg_ccw=30" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_code5_polygon_macro_parameters_and_inch_units(tmp_path: Path):
    path = tmp_path / "macro_polygon_inch.gtl"
    path.write_text(
        "%FSLAX24Y24*%\n"
        "%MOIN*%\n"
        "%AMPOLY*5,1,$1,0,0,$2,$3*%\n"
        "%ADD10POLY,5X0.100X-15*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
        encoding="utf-8",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_regular_polygon_flash(
        0.0,
        0.0,
        2.54,
        5,
        base_rotation_deg=-15.0,
    ).geometry

    assert region_shape(result.regions[0]).symmetric_difference(
        expected
    ).area == pytest.approx(0.0, abs=1e-12)


def test_code5_polygon_macro_d01_uses_exact_convex_sweep(tmp_path: Path):
    path = _write(
        tmp_path,
        "5,1,6,0,0,1,15",
        "X000000Y000000D02*\nX010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_regular_polygon_track(
        0.0,
        0.0,
        1.0,
        0.0,
        1.0,
        6,
        base_rotation_deg=15.0,
    ).geometry

    assert result.tracks == []
    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).symmetric_difference(
        expected
    ).area == pytest.approx(0.0, abs=1e-12)
    assert any(
        evidence.kind == "gerber_polygon_track"
        and "method=convex_sweep_exact" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_code5_polygon_macro_is_preflight_ready(tmp_path: Path):
    path = _write(tmp_path, "5,1,8,0,0,2,0", "X000000Y000000D03*\n")

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


@pytest.mark.parametrize(
    "macro_body",
    [
        "5,0,6,0,0,2,0",
        "5,1,2,0,0,2,0",
        "5,1,13,0,0,2,0",
        "5,1,5.5,0,0,2,0",
        "5,1,6,0.1,0,2,0",
        "5,1,6,0,0.1,2,0",
        "5,1,6,0,0,0,0",
        "5,1,6,0,0,-1,0",
    ],
)
def test_code5_polygon_macro_non_exact_cases_fail_closed(
    tmp_path: Path,
    macro_body: str,
):
    path = _write(tmp_path, macro_body, "X000000Y000000D03*\n")

    with pytest.raises(
        UnsupportedFeatureError,
        match="polygon aperture macro",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_APERTURE_MACRO" in blocker
        for blocker in report.strict_blockers
    )


def test_code5_polygon_macro_with_wrong_modifier_count_is_invalid(tmp_path: Path):
    path = _write(tmp_path, "5,1,6,0,0", "X000000Y000000D03*\n")

    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(path)
