from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


def _write(tmp_path: Path, fs: str, body: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(
        fs + "\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        + body
        + "M02*\n",
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize("fs", ["%FSLIX24Y24*%", "%FSTIX24Y24*%"])
def test_incremental_fs_notation_fails_closed_in_strict_mode(
    tmp_path: Path,
    fs: str,
):
    path = _write(
        tmp_path,
        fs,
        "X010000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="FS incremental coordinate notation is not implemented",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_incremental_fs_notation_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLIX24Y24*%",
        "X010000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(
        diagnostic.code == "GERBER_INCREMENTAL_COORDINATES_UNSUPPORTED"
        for diagnostic in result.diagnostics
    )
    assert not any(
        diagnostic.code == "UNKNOWN_GERBER_STATEMENT"
        for diagnostic in result.diagnostics
    )


def test_absolute_fs_notation_remains_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%",
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 1


def test_preflight_blocks_incremental_fs_notation(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLIX24Y24*%",
        "X010000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "GERBER_INCREMENTAL_COORDINATES_UNSUPPORTED" in blocker
        for blocker in report.strict_blockers
    )
