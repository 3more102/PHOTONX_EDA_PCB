from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.preflight import preflight


HEADER = """M48
METRIC
T01C0.600
%
T01
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "m30.drl"
    path.write_text(HEADER + body, encoding="utf-8")
    return path


def test_clean_m30_terminates_excellon_file(tmp_path: Path):
    path = _write(
        tmp_path,
        "X1.000Y1.000\n"
        "M30\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.drills) == 1
    assert result.diagnostics == []


def test_blank_lines_after_m30_are_ignored(tmp_path: Path):
    path = _write(
        tmp_path,
        "X1.000Y1.000\n"
        "M30\n"
        "\n"
        "\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.drills) == 1
    assert result.diagnostics == []


def test_strict_parser_rejects_data_after_m30(tmp_path: Path):
    path = _write(
        tmp_path,
        "X1.000Y1.000\n"
        "M30\n"
        "X2.000Y2.000\n",
    )

    with pytest.raises(ParseError, match="data after M30 end-of-file command"):
        ExcellonParser(strict=True).parse(path)


def test_permissive_parser_suppresses_geometry_after_m30(tmp_path: Path):
    path = _write(
        tmp_path,
        "X1.000Y1.000\n"
        "M30\n"
        "X2.000Y2.000\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert any(
        diagnostic.code == "INVALID_EXCELLON_DATA_AFTER_M30"
        and diagnostic.line == 9
        for diagnostic in result.diagnostics
    )


def test_preflight_blocks_data_after_m30(tmp_path: Path):
    path = _write(
        tmp_path,
        "X1.000Y1.000\n"
        "M30\n"
        "X2.000Y2.000\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_EXCELLON_DATA_AFTER_M30" in blocker
        for blocker in report.strict_blockers
    )
