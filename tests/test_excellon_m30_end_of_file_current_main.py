import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.preflight import preflight


def _write_program(tmp_path, name: str, trailing: str = ""):
    path = tmp_path / name
    path.write_text(
        "M48\n"
        "METRIC\n"
        "T01C0.8\n"
        "%\n"
        "T01\n"
        "X1.0Y1.0\n"
        "M30\n"
        + trailing,
        encoding="utf-8",
    )
    return path


def test_m30_terminates_valid_excellon_program(tmp_path):
    path = _write_program(tmp_path, "valid.drl")
    result = ExcellonParser().parse(path)

    assert len(result.drills) == 1
    assert result.diagnostics == []


@pytest.mark.parametrize("trailing", ["X2.0Y2.0\n", "; trailing comment\n", "M30\n"])
def test_strict_parser_rejects_nonempty_data_after_m30(tmp_path, trailing):
    path = _write_program(tmp_path, "trailing.drl", trailing)

    with pytest.raises(ParseError, match="data after Excellon M30"):
        ExcellonParser().parse(path)


def test_permissive_parser_fails_closed_after_m30(tmp_path):
    path = _write_program(tmp_path, "trailing.drl", "X2.0Y2.0\n")

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert [d.code for d in result.diagnostics] == [
        "EXCELLON_TRAILING_DATA_AFTER_M30"
    ]


def test_preflight_blocks_data_after_m30(tmp_path):
    path = _write_program(tmp_path, "trailing.drl", "X2.0Y2.0\n")

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.files[0].strict_blockers == [
        "EXCELLON_TRAILING_DATA_AFTER_M30"
    ]
    assert not report.ready_for_strict_reconstruction


def test_blank_lines_after_m30_are_ignored(tmp_path):
    path = _write_program(tmp_path, "blank-tail.drl", "\n\n")

    result = ExcellonParser().parse(path)

    assert len(result.drills) == 1
    assert result.diagnostics == []
