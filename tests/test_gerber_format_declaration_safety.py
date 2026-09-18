from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "format.gtl"
    path.write_text(body, encoding="utf-8")
    return path


def test_coordinate_before_fs_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "%MOMM*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    with pytest.raises(ParseError, match="before explicit FS declaration"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_missing_fs_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%MOMM*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(
        diagnostic.code == "GERBER_FORMAT_UNDECLARED"
        for diagnostic in result.diagnostics
    )


def test_late_fs_does_not_reenable_suppressed_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%MOMM*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "%FSLAX24Y24*%\n"
        "X020000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []


def test_duplicate_same_fs_declaration_remains_tolerated(tmp_path: Path):
    path = _write(
        tmp_path,
        "%MOMM*%\n"
        "%FSLAX24Y24*%\n"
        "%FSLAX24Y24*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1


def test_conflicting_fs_declaration_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "%MOMM*%\n"
        "%FSLAX24Y24*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "%FSLAX25Y25*%\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="coordinate format changed"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_conflicting_fs_declaration_clears_prior_permissive_geometry(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%MOMM*%\n"
        "%FSLAX24Y24*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "%FSLAX25Y25*%\n"
        "X0200000Y0100000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(
        diagnostic.code == "CONFLICTING_GERBER_FORMAT"
        for diagnostic in result.diagnostics
    )


def test_declared_fs_controls_coordinate_scaling(tmp_path: Path):
    path = _write(
        tmp_path,
        "%MOMM*%\n"
        "%FSLAX25Y25*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X0100000Y0000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert result.pads[0].center.x == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("body", "expected_code"),
    [
        (
            "%MOMM*%\n"
            "%ADD10C,0.500*%\n"
            "D10*\n"
            "X010000Y010000D03*\n"
            "M02*\n",
            "GERBER_FORMAT_UNDECLARED",
        ),
        (
            "%MOMM*%\n"
            "%FSLAX24Y24*%\n"
            "%FSLAX25Y25*%\n"
            "M02*\n",
            "CONFLICTING_GERBER_FORMAT",
        ),
    ],
)
def test_preflight_blocks_unsafe_coordinate_format_semantics(
    tmp_path: Path,
    body: str,
    expected_code: str,
):
    path = _write(tmp_path, body)

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(expected_code in blocker for blocker in report.strict_blockers)
