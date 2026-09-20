from pathlib import Path

from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


HEADER = """%FSLAX24Y24*%
%MOMM*%
"""


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(HEADER + body, encoding="utf-8")
    return path


def _details(obj, kind: str) -> list[str]:
    return [
        item.detail
        for item in obj.provenance.evidence
        if item.kind == kind
    ]


def test_x2_aperture_attributes_are_frozen_at_ad_and_survive_later_td(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "aperture_attributes.gtl",
        """%TA.AperFunction,Conductor*%
%ADD10C,0.500*%
%TA.AperFunction,ViaPad*%
%ADD11C,0.800*%
%TD.AperFunction*%
%ADD12C,0.300*%
D10*
X010000Y010000D03*
D11*
X020000Y010000D03*
D12*
X030000Y010000D03*
D10*
X040000Y010000D03*
M02*
""",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 4
    assert _details(result.pads[0], "gerber_x2_aperture_function") == [
        "Conductor"
    ]
    assert _details(result.pads[1], "gerber_x2_aperture_function") == [
        "ViaPad"
    ]
    assert _details(result.pads[2], "gerber_x2_aperture_function") == []
    assert _details(result.pads[3], "gerber_x2_aperture_function") == [
        "Conductor"
    ]
    assert _details(result.pads[0], "gerber_x2_aperture_attribute") == [
        "name=.AperFunction; values=('Conductor',)"
    ]


def test_x2_region_inherits_live_aperture_attribute_dictionary(tmp_path: Path):
    path = _write(
        tmp_path,
        "region_attribute.gtl",
        """%TA.AperFunction,Conductor*%
G36*
X000000Y000000D02*
X010000Y000000D01*
X010000Y010000D01*
X000000Y010000D01*
X000000Y000000D01*
G37*
%TD.AperFunction*%
M02*
""",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    assert _details(result.regions[0], "gerber_x2_aperture_function") == [
        "Conductor"
    ]


def test_user_aperture_attribute_is_preserved_exactly_on_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "user_attribute.gtl",
        """%TA.myMeta,alpha,beta*%
%ADD10C,0.500*%
D10*
X010000Y010000D03*
M02*
""",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert _details(result.pads[0], "gerber_x2_aperture_attribute") == [
        "name=myMeta; values=('alpha', 'beta')"
    ]
