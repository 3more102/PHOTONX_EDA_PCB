from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


BASE = """%FSLAX24Y24*%
%MOMM*%
%ADD10R,0.600X0.300*%
D10*
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(BASE + body + "M02*\n", encoding="utf-8")
    return path


@pytest.mark.parametrize("command", ["%LMN*%", "%LR0*%", "%LR360*%", "%LS1*%"])
def test_identity_aperture_transforms_keep_supported_geometry(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    pad = result.pads[0]
    assert pad.size_x == pytest.approx(0.6)
    assert pad.size_y == pytest.approx(0.3)


@pytest.mark.parametrize(
    ("command", "label"),
    [
        ("%LMX*%", "mirroring"),
        ("%LR90*%", "rotation"),
        ("%LS2*%", "scaling"),
    ],
)
def test_non_identity_aperture_transforms_fail_closed_in_strict_mode(
    tmp_path: Path,
    command: str,
    label: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X010000Y020000D03*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match=rf"aperture {label}",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_non_identity_transform_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LR90*%\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert result.tracks == []
    assert result.outline == []
    assert any(
        diagnostic.code == "UNSUPPORTED_GERBER_APERTURE_TRANSFORM"
        for diagnostic in result.diagnostics
    )


def test_late_transform_clears_prior_geometry_and_identity_does_not_reenable(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "X010000Y020000D03*\n"
        "%LS2*%\n"
        "X020000Y020000D03*\n"
        "%LS1*%\n"
        "X030000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert result.tracks == []
    assert result.outline == []


def test_non_positive_scaling_is_invalid(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LS0*%\n"
        "X010000Y020000D03*\n",
    )

    with pytest.raises(ParseError, match="greater than zero"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_malformed_aperture_transform_is_invalid_and_suppressed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LRABC*%\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert any(
        diagnostic.code == "INVALID_GERBER_APERTURE_TRANSFORM"
        for diagnostic in result.diagnostics
    )


def test_preflight_blocks_non_identity_aperture_transform(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LMY*%\n"
        "X010000Y020000D03*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_APERTURE_TRANSFORM" in blocker
        for blocker in report.strict_blockers
    )
