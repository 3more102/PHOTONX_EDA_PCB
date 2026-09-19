from pathlib import Path

import pytest

from photonx_eda_pcb.parsers.common.attributes import validate_x2_attribute_command
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(body, encoding="utf-8")
    return path


def _details(obj, kind: str) -> list[str]:
    return [
        item.detail
        for item in obj.provenance.evidence
        if item.kind == kind
    ]


def test_to_p_is_snapshotted_as_structured_component_pin_evidence(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "%TO.P,U1,1,GND*%\n"
        "X010000Y010000D03*\n"
        "%TO.P,U1,2,OUT*%\n"
        "X020000Y010000D03*\n"
        "%TD.P*%\n"
        "X030000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 3
    first, second, third = result.pads

    assert _details(first, "gerber_x2_component_refdes") == ["U1"]
    assert _details(first, "gerber_x2_pin_number") == ["1"]
    assert _details(first, "gerber_x2_pin_function") == ["GND"]

    assert _details(second, "gerber_x2_component_refdes") == ["U1"]
    assert _details(second, "gerber_x2_pin_number") == ["2"]
    assert _details(second, "gerber_x2_pin_function") == ["OUT"]

    assert _details(third, "gerber_x2_component_refdes") == []
    assert _details(third, "gerber_x2_pin_number") == []
    assert _details(third, "gerber_x2_pin_function") == []


def test_to_p_allows_spec_defined_empty_pin_number(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "%TO.P,U3,*%\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert _details(result.pads[0], "gerber_x2_component_refdes") == ["U3"]
    assert _details(result.pads[0], "gerber_x2_pin_number") == [""]
    assert _details(result.pads[0], "gerber_x2_pin_function") == []


@pytest.mark.parametrize(
    "text",
    [
        "%TO.P*%",
        "%TO.P,U1*%",
        "%TO.P,U1,1,GND,EXTRA*%",
    ],
)
def test_to_p_rejects_invalid_field_cardinality(text: str):
    with pytest.raises(ValueError):
        validate_x2_attribute_command(text)


def test_to_p_accepts_optional_pin_function():
    assert validate_x2_attribute_command("%TO.P,U1,7,RESET*%") == (
        "TO",
        ".P",
        ["U1", "7", "RESET"],
    )
