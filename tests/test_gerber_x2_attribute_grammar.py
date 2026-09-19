from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.common.attributes import validate_x2_attribute_command
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(body, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "%TF.GenerationSoftware,Ucamco,UcamX,2026.06*%",
            (
                "TF",
                ".GenerationSoftware",
                ["Ucamco", "UcamX", "2026.06"],
            ),
        ),
        (
            r"%TF.GenerationSoftware,Vendor\u002CInc,Tool,1.0*%",
            (
                "TF",
                ".GenerationSoftware",
                ["Vendor,Inc", "Tool", "1.0"],
            ),
        ),
        (
            "%TA.AperFunction,Conductor*%",
            ("TA", ".AperFunction", ["Conductor"]),
        ),
        ("%TO.P,U1,1*%", ("TO", ".P", ["U1", "1"])),
        ("%TFVendorMeta,alpha,beta*%", ("TF", "VendorMeta", ["alpha", "beta"])),
        ("%TD*%", ("TD", "", [])),
        ("%TD.AperFunction*%", ("TD", ".AperFunction", [])),
    ],
)
def test_validate_x2_attribute_command_accepts_2026_05_grammar(text, expected):
    assert validate_x2_attribute_command(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "%TA.FileFunction,Copper,L1,Top*%",
        "%TF.AperFunction,Conductor*%",
        "%TO.UnknownStandard,value*%",
        "%TDBad Name*%",
        "%TD.AperFunction,Conductor*%",
        "%TO.C*%",
    ],
)
def test_validate_x2_attribute_command_rejects_invalid_domain_or_shape(text):
    with pytest.raises(ValueError):
        validate_x2_attribute_command(text)


def test_production_parser_rejects_wrong_standard_attribute_domain(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TA.FileFunction,Copper,L1,Top*%\n"
        "M02*\n",
    )

    with pytest.raises(ParseError, match="invalid Gerber X2 attribute command"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_valid_user_attribute_remains_preserved_as_diagnostic(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TFVendorMeta,alpha,beta*%\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert any(
        diagnostic.code == "GERBER_ATTRIBUTE_PRESERVED_AS_DIAGNOSTIC"
        and diagnostic.message == "%TFVendorMeta,alpha,beta*%"
        for diagnostic in result.diagnostics
    )


def test_permissive_invalid_x2_attribute_suppresses_file_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%TA.FileFunction,Copper,L1,Top*%\n"
        "X020000Y000000D01*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.regions == []
    assert result.outline == []
    assert any(
        diagnostic.code == "INVALID_GERBER_X2_ATTRIBUTE"
        for diagnostic in result.diagnostics
    )
