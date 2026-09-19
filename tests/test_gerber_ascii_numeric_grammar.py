from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.gerber_parts.format_spec import parse_format_spec
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


def _write(tmp_path: Path, lines: list[str]) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


@pytest.mark.parametrize(
    "statement",
    [
        "%FSLAX٢٤Y24*%",
        "%FSLAX2４Y24*%",
    ],
)
def test_format_spec_helper_rejects_non_ascii_decimal_digits(statement: str):
    with pytest.raises(ValueError, match="invalid Gerber format specification"):
        parse_format_spec(statement)


@pytest.mark.parametrize(
    "bad_statement",
    [
        "%FSLAX٢٤Y24*%",
        "%ADD١٠C,0.200*%",
        "D١٠*",
        "G54D١٠*",
    ],
)
def test_production_parser_rejects_non_ascii_structured_numeric_tokens(
    tmp_path: Path,
    bad_statement: str,
):
    path = _write(
        tmp_path,
        [
            "%FSLAX24Y24*%",
            "%MOMM*%",
            "%ADD10C,0.200*%",
            "D10*",
            "X010000Y010000D03*",
            bad_statement,
            "M02*",
        ],
    )

    with pytest.raises(ParseError, match="ASCII decimal digits"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_permissive_unicode_aperture_selection_clears_geometry(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        [
            "%FSLAX24Y24*%",
            "%MOMM*%",
            "%ADD10C,0.200*%",
            "%ADD11C,1.000*%",
            "D10*",
            "X010000Y010000D03*",
            "D١١*",
            "X020000Y020000D03*",
            "M02*",
        ],
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert result.tracks == []
    assert result.regions == []
    assert result.outline == []
    assert any(
        diagnostic.code == "INVALID_GERBER_NUMERIC_TOKEN"
        for diagnostic in result.diagnostics
    )


@pytest.mark.parametrize(
    "bad_statement",
    [
        "%FSLAX٢٤Y24*%",
        "%ADD١٠C,0.200*%",
    ],
)
def test_permissive_unicode_format_or_aperture_token_suppresses_file_geometry(
    tmp_path: Path,
    bad_statement: str,
):
    path = _write(
        tmp_path,
        [
            "%FSLAX24Y24*%",
            "%MOMM*%",
            "%ADD10C,0.200*%",
            "D10*",
            "X010000Y010000D03*",
            bad_statement,
            "X020000Y020000D03*",
            "M02*",
        ],
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert any(
        diagnostic.code == "INVALID_GERBER_NUMERIC_TOKEN"
        for diagnostic in result.diagnostics
    )
