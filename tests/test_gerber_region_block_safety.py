from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


BASE = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,0.200*%
D10*
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(BASE + body + "M02*\n", encoding="utf-8")
    return path


def test_region_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "G36*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "X010000Y010000D01*\n"
        "X000000Y000000D01*\n"
        "G37*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="regions/aperture blocks are not implemented safely",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_region_body_does_not_leak_tracks_in_permissive_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "G36*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "X010000Y010000D01*\n"
        "X000000Y000000D01*\n"
        "G37*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(
        diagnostic.code == "UNSUPPORTED_GERBER_CONSTRUCT"
        for diagnostic in result.diagnostics
    )


def test_aperture_block_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ABD11*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%AB*%\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="regions/aperture blocks are not implemented safely",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_aperture_block_body_does_not_leak_geometry_in_permissive_mode(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%ABD11*%\n"
        "X010000Y010000D03*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%AB*%\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []


def test_late_region_clears_prior_geometry_and_never_reenables(tmp_path: Path):
    path = _write(
        tmp_path,
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "G36*\n"
        "X020000Y000000D02*\n"
        "X030000Y000000D01*\n"
        "G37*\n"
        "X040000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []


@pytest.mark.parametrize(
    "construct",
    [
        "G36*\nG37*\n",
        "%ABD11*%\n%AB*%\n",
    ],
)
def test_preflight_blocks_regions_and_aperture_blocks(
    tmp_path: Path,
    construct: str,
):
    path = _write(tmp_path, construct)

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_CONSTRUCT" in blocker
        for blocker in report.strict_blockers
    )
