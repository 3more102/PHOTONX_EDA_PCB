from pathlib import Path

import pytest

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


@pytest.mark.parametrize(
    ("fs", "one", "half"),
    [
        ("%FSLIX24Y24*%", "010000", "005000"),
        ("%FSTIX24Y24*%", "01", "005"),
    ],
)
def test_incremental_fs_notation_accumulates_xy_deltas(
    tmp_path: Path,
    fs: str,
    one: str,
    half: str,
):
    path = _write(
        tmp_path,
        fs,
        f"X{one}Y{one}D02*\n"
        f"X{one}D01*\n"
        f"Y-{half}D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 2
    assert result.tracks[0].start == pytest.approx((1.0, 1.0))
    assert result.tracks[0].end == pytest.approx((2.0, 1.0))
    assert result.tracks[1].end == pytest.approx((2.0, 0.5))


def test_g90_switches_incremental_fs_file_back_to_absolute_notation(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%FSLIX24Y24*%",
        "X010000Y010000D02*\n"
        "G90*\n"
        "X030000Y040000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert (result.pads[0].center.x, result.pads[0].center.y) == pytest.approx(
        (3.0, 4.0)
    )


def test_incremental_fs_arc_endpoint_accumulates_but_ij_remains_offset(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%FSLIX24Y24*%",
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X-010000Y010000I-010000J000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks
    assert result.tracks[0].start == pytest.approx((1.0, 0.0))
    assert result.tracks[-1].end == pytest.approx((0.0, 1.0))


def test_absolute_fs_notation_remains_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%",
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 1


@pytest.mark.parametrize("fs", ["%FSLIX24Y24*%", "%FSTIX24Y24*%"])
def test_preflight_accepts_supported_incremental_fs_notation(
    tmp_path: Path,
    fs: str,
):
    body = (
        "X010000Y000000D02*\nX010000Y000000D01*\n"
        if fs.startswith("%FSLI")
        else "X01Y0D02*\nX01Y0D01*\n"
    )
    path = _write(tmp_path, fs, body)

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not any(
        "GERBER_INCREMENTAL_COORDINATES_UNSUPPORTED" in blocker
        for blocker in report.strict_blockers
    )
