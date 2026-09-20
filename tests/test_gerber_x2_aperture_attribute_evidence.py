from pathlib import Path

from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(body, encoding="utf-8")
    return path


def _evidence(obj, kind: str) -> list[str]:
    return [
        item.detail
        for item in obj.provenance.evidence
        if item.kind == kind
    ]


def test_ta_snapshot_is_fixed_on_aperture_and_td_is_not_retroactive(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TA.AperFunction,SMDPad,CuDef*%\n"
        "%ADD10C,1.000*%\n"
        "%TD.AperFunction*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    pad = result.pads[0]
    assert _evidence(pad, "gerber_x2_aperture_function") == ["SMDPad,CuDef"]
    assert any(
        "name=.AperFunction" in detail and "SMDPad" in detail
        for detail in _evidence(pad, "gerber_x2_aperture_attribute")
    )


def test_each_add_gets_its_own_ta_snapshot(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TA.AperFunction,SMDPad,CuDef*%\n"
        "%ADD10C,1.000*%\n"
        "%TA.AperFunction,Conductor*%\n"
        "%ADD11C,0.200*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "D11*\n"
        "X020000Y000000D02*\n"
        "X030000Y000000D01*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert _evidence(result.pads[0], "gerber_x2_aperture_function") == ["SMDPad,CuDef"]
    assert _evidence(result.tracks[0], "gerber_x2_aperture_function") == [
        "Conductor"
    ]


def test_region_uses_ta_dictionary_at_g36_not_selected_aperture(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TA.AperFunction,ViaPad*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "%TA.AperFunction,Conductor*%\n"
        "G36*\n"
        "X000000Y000000D02*\n"
        "X020000Y000000D01*\n"
        "X020000Y010000D01*\n"
        "X000000Y010000D01*\n"
        "X000000Y000000D01*\n"
        "G37*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    functions = _evidence(result.regions[0], "gerber_x2_aperture_function")
    assert functions == ["Conductor"]
    assert "ViaPad" not in functions


def test_td_without_name_clears_ta_and_to_state_for_future_creations(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TA.AperFunction,SMDPad,CuDef*%\n"
        "%TO.N,CLK*%\n"
        "%TD*%\n"
        "%ADD10C,1.000*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert _evidence(pad, "gerber_x2_aperture_attribute") == []
    assert _evidence(pad, "gerber_x2_aperture_function") == []
    assert _evidence(pad, "gerber_x2_object_attribute") == []
    assert _evidence(pad, "gerber_x2_net_name") == []

def test_custom_name_switches_domain_without_rewriting_frozen_aperture(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TAUserAttr,APERTURE*%\n"
        "%ADD10C,1.000*%\n"
        "%TOUserAttr,OBJECT*%\n"
        "%ADD11C,1.000*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "D11*\n"
        "X020000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    first, second = result.pads
    assert any(
        "name=UserAttr" in detail and "APERTURE" in detail
        for detail in _evidence(first, "gerber_x2_aperture_attribute")
    )
    assert any(
        "name=UserAttr" in detail and "OBJECT" in detail
        for detail in _evidence(first, "gerber_x2_object_attribute")
    )
    assert _evidence(second, "gerber_x2_aperture_attribute") == []
    assert any(
        "name=UserAttr" in detail and "OBJECT" in detail
        for detail in _evidence(second, "gerber_x2_object_attribute")
    )




def test_incomplete_smdpad_function_remains_generic_evidence_only(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TA.AperFunction,SMDPad*%\n"
        "%ADD10C,1.000*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert _evidence(pad, "gerber_x2_aperture_function") == []
    generic = _evidence(pad, "gerber_x2_aperture_attribute")
    assert len(generic) == 1
    assert "name=.AperFunction" in generic[0]
    assert "SMDPad" in generic[0]


def test_unknown_aperture_function_remains_generic_evidence_only(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TA.AperFunction,MadeUpFunction*%\n"
        "%ADD10C,1.000*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert _evidence(pad, "gerber_x2_aperture_function") == []
    generic = _evidence(pad, "gerber_x2_aperture_attribute")
    assert len(generic) == 1
    assert "MadeUpFunction" in generic[0]


def test_valid_smdpad_function_with_required_qualifier_is_structured(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TA.AperFunction,SMDPad,SMDef*%\n"
        "%ADD10C,1.000*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert _evidence(
        result.pads[0], "gerber_x2_aperture_function"
    ) == ["SMDPad,SMDef"]
