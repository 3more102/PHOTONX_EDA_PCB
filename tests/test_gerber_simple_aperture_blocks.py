from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(
        "%FSLAX24Y24*%\n%MOMM*%\n" + body + "M02*\n",
        encoding="utf-8",
    )
    return path


def test_single_origin_flash_aperture_block_reduces_exactly(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,1.000*%\n"
        "%ABD11*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "%AB*%\n"
        "D11*\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks == []
    assert result.regions == []
    assert len(result.pads) == 1
    pad = result.pads[0]
    assert pad.center.x == pytest.approx(1.0)
    assert pad.center.y == pytest.approx(2.0)
    assert pad.size_x == pytest.approx(1.0)
    assert pad.size_y == pytest.approx(1.0)
    assert pad.shape == "C"
    assert any(
        diagnostic.code == "GERBER_APERTURE_BLOCK_REDUCED"
        for diagnostic in result.diagnostics
    )


def test_aperture_block_preserves_supported_holed_flash_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10R,1.200X0.800X0.300*%\n"
        "%ABD11*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "%AB*%\n"
        "D11*\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.pads == []
    assert len(result.regions) == 1
    assert len(result.regions[0].holes) == 1


def test_off_origin_aperture_block_member_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,1.000*%\n"
        "%ABD11*%\n"
        "D10*\n"
        "X000100Y000000D03*\n"
        "%AB*%\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="off-origin aperture-block members",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_composite_aperture_block_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,1.000*%\n"
        "%ABD11*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "X000000Y000000D03*\n"
        "%AB*%\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="composite aperture blocks",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_aperture_block_inside_region_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,1.000*%\n"
        "G36*\n"
        "X000000Y000000D02*\n"
        "%ABD11*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "%AB*%\n"
        "G37*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="no active G36 region",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_aperture_block_definition_rejects_legacy_image_transform(tmp_path: Path):
    path = _write(
        tmp_path,
        "%IR90*%\n"
        "%ADD10C,1.000*%\n"
        "%ABD11*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "%AB*%\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="identity LM/LR/LS and MI/SF/OF/IR state",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_permissive_unsupported_block_cannot_leak_body_or_surrounding_geometry(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%ADD10C,1.000*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "%ABD11*%\n"
        "D10*\n"
        "X000100Y000000D03*\n"
        "%AB*%\n"
        "X020000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.regions == []
    assert result.outline == []
    assert any(
        diagnostic.code == "UNSUPPORTED_GERBER_APERTURE_BLOCK"
        for diagnostic in result.diagnostics
    )


def test_preflight_accepts_exact_single_flash_aperture_block(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,1.000*%\n"
        "%ABD11*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "%AB*%\n"
        "D11*\n"
        "X010000Y020000D03*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert report.strict_blockers == []


def test_unterminated_aperture_block_fails_closed(tmp_path: Path):
    path = tmp_path / "top.gtl"
    path.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,1.000*%\n"
        "%ABD11*%\n"
        "D10*\n"
        "X000000Y000000D03*\n",
        encoding="utf-8",
    )

    with pytest.raises(ParseError, match="unterminated aperture block"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)
