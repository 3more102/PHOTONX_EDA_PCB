from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.preflight import preflight


def _write_program(path: Path, unknown: str = "M99") -> Path:
    path.write_text(
        "M48\n"
        "METRIC\n"
        "T01C0.800\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        f"{unknown}\n"
        "X2.000Y2.000\n"
        "M30\n"
    )
    return path


def test_unknown_excellon_statement_is_rejected_in_strict_mode(tmp_path: Path):
    path = _write_program(tmp_path / "unknown.drl")

    with pytest.raises(ParseError, match="unrecognized Excellon statement"):
        ExcellonParser(strict=True).parse(path)


def test_unknown_excellon_statement_suppresses_permissive_geometry(tmp_path: Path):
    path = _write_program(tmp_path / "unknown.drl")

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert [d.code for d in result.diagnostics] == ["UNKNOWN_EXCELLON_STATEMENT"]


def test_unknown_excellon_statement_remains_a_preflight_blocker(tmp_path: Path):
    _write_program(tmp_path / "unknown.drl")

    report = preflight(tmp_path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNKNOWN_EXCELLON_STATEMENT" in blocker
        for blocker in report.strict_blockers
    )
