from __future__ import annotations

from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser


HEADER = "M48\nMETRIC\nT01C0.800\n%\nT01\n"


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "program_end.drl"
    path.write_text(HEADER + body, encoding="utf-8")
    return path


@pytest.mark.parametrize("terminator", ["M30", "M00"])
@pytest.mark.parametrize("strict", [True, False])
def test_program_termination_ignores_trailing_content(
    tmp_path: Path, terminator: str, strict: bool
) -> None:
    path = _write(
        tmp_path,
        (
            "X1.000Y1.000\n"
            f"{terminator}\n"
            "X2.000Y2.000\n"
            "THIS_IS_NOT_EXCELLON\n"
        ),
    )

    result = ExcellonParser(strict=strict).parse(path)

    assert len(result.drills) == 1
    assert result.drills[0].center.x == pytest.approx(1.0)
    assert result.drills[0].center.y == pytest.approx(1.0)
    assert not result.diagnostics


@pytest.mark.parametrize("terminator", ["M30", "M00"])
def test_program_termination_does_not_hide_unfinished_route(
    tmp_path: Path, terminator: str
) -> None:
    path = _write(
        tmp_path,
        (
            "G00X1.000Y1.000\n"
            "M15\n"
            "G01X2.000Y1.000\n"
            f"{terminator}\n"
            "M16\n"
        ),
    )

    with pytest.raises(ParseError, match="EOF while route tool is down"):
        ExcellonParser(strict=True).parse(path)

    permissive = ExcellonParser(strict=False).parse(path)
    assert not permissive.routes
    assert any(
        diagnostic.code == "EXCELLON_ROUTE_UNTERMINATED"
        for diagnostic in permissive.diagnostics
    )
