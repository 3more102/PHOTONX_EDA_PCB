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


@pytest.mark.parametrize(
    "command",
    [
        "%MIA1B0*%",
        "%OFA1B0*%",
        "%ASAYBX*%",
        "%IPNEG*%",
    ],
)
def test_non_default_legacy_transforms_fail_closed_in_strict_mode(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="changes image geometry",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


@pytest.mark.parametrize(
    "command",
    [
        "%ASAXBY*%",
        "%IPPOS*%",
        "%MIA0B0*%",
        "%OFA0B0*%",
    ],
)
def test_identity_legacy_transforms_keep_supported_geometry(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 1


def test_non_default_legacy_transform_suppresses_permissive_geometry(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%MIA1B0*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(
        diagnostic.code == "UNSUPPORTED_GERBER_TRANSFORM"
        for diagnostic in result.diagnostics
    )


def test_late_legacy_transform_clears_prior_geometry_and_never_reenables(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%OFA1B0*%\n"
        "X020000Y000000D01*\n"
        "%OFA0B0*%\n"
        "X030000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []


def test_preflight_blocks_non_default_legacy_transform(tmp_path: Path):
    path = _write(
        tmp_path,
        "%IPNEG*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_TRANSFORM" in blocker
        for blocker in report.strict_blockers
    )
