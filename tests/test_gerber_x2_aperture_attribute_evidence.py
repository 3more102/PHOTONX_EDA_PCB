from pathlib import Path

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


def test_ta_aperture_function_is_fixed_at_aperture_definition(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TA.AperFunction,SMDPad*%\n"
        "%ADD10C,0.500*%\n"
        "%TD.AperFunction*%\n"
        "%TA.AperFunction,Conductor*%\n"
        "%ADD11C,0.200*%\n"
        "%TD*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "D11*\n"
        "X020000Y010000D02*\n"
        "X030000Y010000D01*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert len(result.tracks) == 1
    assert _details(result.pads[0], "gerber_x2_aperture_function") == ["SMDPad"]
    assert _details(result.tracks[0], "gerber_x2_aperture_function") == [
        "Conductor"
    ]
    assert any(
        item.kind == "gerber_x2_aperture_attribute"
        and "aperture=D10" in item.detail
        and "name=.AperFunction" in item.detail
        for item in result.pads[0].provenance.evidence
    )


def test_ta_after_aperture_definition_is_not_retroactive(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.500*%\n"
        "%TA.AperFunction,SMDPad*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert _details(result.pads[0], "gerber_x2_aperture_function") == []
    assert _details(result.pads[0], "gerber_x2_aperture_attribute") == []


def test_user_aperture_attribute_is_preserved_as_generic_evidence(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TAVendorTag,laser_defined*%\n"
        "%ADD10C,0.500*%\n"
        "%TDVendorTag*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    details = _details(result.pads[0], "gerber_x2_aperture_attribute")
    assert len(details) == 1
    assert "name=VendorTag" in details[0]
    assert "laser_defined" in details[0]


def test_macro_aperture_snapshots_ta_attributes_too(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMROUND*1,1,$1,0,0*%\n"
        "%TA.AperFunction,SMDPad*%\n"
        "%ADD10ROUND,0.500*%\n"
        "%TD*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert _details(result.pads[0], "gerber_x2_aperture_function") == ["SMDPad"]
