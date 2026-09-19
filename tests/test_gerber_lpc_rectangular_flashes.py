from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.geometry_kernel import region_shape
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


HEADER = "%FSLAX24Y24*%\n%MOMM*%\n"


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(HEADER + body + "M02*\n", encoding="utf-8")
    return path


def _rectangle_region(x0: str, y0: str, x1: str, y1: str) -> str:
    return (
        "G36*\n"
        f"X{x0}Y{y0}D02*\n"
        f"X{x1}Y{y0}D01*\n"
        f"X{x1}Y{y1}D01*\n"
        f"X{x0}Y{y1}D01*\n"
        f"X{x0}Y{y0}D01*\n"
        "G37*\n"
    )


def test_lpc_rectangular_flash_subtracts_exact_hole(tmp_path: Path):
    path = _write(
        tmp_path,
        "rect_flash_hole.gtl",
        "%ADD10R,10X10*%\n"
        "%ADD11R,4X4*%\n"
        "%LPD*%\n"
        "D10*\n"
        "X050000Y050000D03*\n"
        "%LPC*%\n"
        "D11*\n"
        "X050000Y050000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.pads == []
    assert len(result.regions) == 1
    assert len(result.regions[0].holes) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(84.0)
    assert any(
        evidence.kind == "gerber_layer_polarity_composition"
        for evidence in result.regions[0].provenance.evidence
    )


def test_lpc_clear_rectangular_flash_before_dark_is_noop(tmp_path: Path):
    path = _write(
        tmp_path,
        "clear_before_dark_flash.gtl",
        "%ADD10R,10X10*%\n"
        "%ADD11R,4X4*%\n"
        "%LPC*%\n"
        "D11*\n"
        "X050000Y050000D03*\n"
        "%LPD*%\n"
        "D10*\n"
        "X050000Y050000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.pads == []
    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(100.0)


def test_lpc_dark_flash_can_refill_clear_flash_area(tmp_path: Path):
    path = _write(
        tmp_path,
        "rect_flash_refill.gtl",
        "%ADD10R,10X10*%\n"
        "%ADD11R,4X4*%\n"
        "%ADD12R,2X2*%\n"
        "%LPD*%\n"
        "D10*\n"
        "X050000Y050000D03*\n"
        "%LPC*%\n"
        "D11*\n"
        "X050000Y050000D03*\n"
        "%LPD*%\n"
        "D12*\n"
        "X050000Y050000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.pads == []
    assert len(result.regions) == 2
    assert sum(region_shape(region).area for region in result.regions) == pytest.approx(
        88.0
    )


def test_lpc_region_and_rectangular_flash_compose_in_one_ordered_image(tmp_path: Path):
    path = _write(
        tmp_path,
        "region_plus_clear_flash.gtl",
        "%ADD10R,4X4*%\n"
        "%LPD*%\n"
        + _rectangle_region("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        "D10*\n"
        "X050000Y050000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.pads == []
    assert len(result.regions) == 1
    assert len(result.regions[0].holes) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(84.0)

    report = preflight(path)
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_lpc_rectangular_flash_then_clear_region_preserves_order(tmp_path: Path):
    path = _write(
        tmp_path,
        "flash_plus_clear_region.gtl",
        "%ADD10R,10X10*%\n"
        "%LPD*%\n"
        "D10*\n"
        "X050000Y050000D03*\n"
        "%LPC*%\n"
        + _rectangle_region("020000", "020000", "040000", "040000"),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.pads == []
    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(96.0)


def test_lpc_rectangular_flash_step_repeat_composes_each_instance(tmp_path: Path):
    path = _write(
        tmp_path,
        "rect_flash_sr.gtl",
        "%ADD10R,10X10*%\n"
        "%ADD11R,4X4*%\n"
        "%SRX2Y1I20J0*%\n"
        "%LPD*%\n"
        "D10*\n"
        "X050000Y050000D03*\n"
        "%LPC*%\n"
        "D11*\n"
        "X050000Y050000D03*\n"
        "%SR*%\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.pads == []
    assert len(result.regions) == 2
    assert all(len(region.holes) == 1 for region in result.regions)
    assert sum(region_shape(region).area for region in result.regions) == pytest.approx(
        168.0
    )


def test_lpc_circular_flash_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "circle_flash.gtl",
        "%ADD10C,2*%\n"
        "%LPC*%\n"
        "D10*\n"
        "X050000Y050000D03*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="rectangular D03 flashes",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_CLEAR_POLARITY_NON_RECTANGULAR_FLASH" in blocker
        for blocker in report.strict_blockers
    )

def test_lpc_rectangular_flash_follows_whole_image_rotation(tmp_path: Path):
    path = _write(
        tmp_path,
        "rect_flash_ir90.gtl",
        "%IR90*%\n"
        "%ADD10R,4X2*%\n"
        "%ADD11R,2X1*%\n"
        "%LPD*%\n"
        "D10*\n"
        "X050000Y050000D03*\n"
        "%LPC*%\n"
        "D11*\n"
        "X050000Y050000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.pads == []
    assert len(result.regions) == 1
    region = result.regions[0]
    shape = region_shape(region)
    assert shape.area == pytest.approx(6.0)
    assert shape.bounds == pytest.approx((-6.0, 3.0, -4.0, 7.0))
    assert len(region.holes) == 1

