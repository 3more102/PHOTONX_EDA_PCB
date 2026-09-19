import pytest

from photonx_eda_pcb.parsers.layer_map import infer_layer


@pytest.mark.parametrize(
    ("attribute", "expected"),
    [
        ("%TF.FileFunction,Copper,L1,Top*%", "F.Cu"),
        ("%TF.FileFunction,Copper,L2,Inr,Plane*%", "In1.Cu"),
        ("%TF.FileFunction,Copper,L4,Bot,Signal*%", "B.Cu"),
        ("%TF.FileFunction,Soldermask,Top,2*%", "F.Mask"),
        ("%TF.FileFunction,Legend,Bot*%", "B.SilkS"),
        ("%TF.FileFunction,Paste,Top*%", "F.Paste"),
        ("%TF.FileFunction,Profile,NP*%", "Edge.Cuts"),
        ("G04 #@! TF.FileFunction,Copper,L1,Top*", "F.Cu"),
    ],
)
def test_valid_x2_file_functions(attribute: str, expected: str) -> None:
    assert infer_layer("misleading.gtl", attribute) == expected


@pytest.mark.parametrize(
    "attribute",
    [
        "%TF.FileFunction,Copper,L2*%",
        "%TF.FileFunction,Copper,L1,Inr*%",
        "%TF.FileFunction,Copper,L2,Top*%",
        "%TF.FileFunction,Copper,L2,Inr,UnknownType*%",
        "%TF.FileFunction,Profile*%",
        "%TF.FileFunction,Soldermask,Top,0*%",
        "%TF.FileFunction,Drillmap*%",
        "%TF.FileFunction*%",
        "%TF.FileFunction,Copper,L1,,Top*%",
        "%TF.FileFunction,Outline,Top*%",
        "%TF.FileFunction,Copper,L1,Top*%\n%TF.FileFunction,Copper,L2,Bot*%",
        "%TF.FileFunction,Copper,L1,Top*%\n%TF.FileFunction*%",
        "G04 #@! TF.FileFunction*",
        "%TF.FileFunction,Copper,L1,Top*%\nG04 #@! TF.FileFunction,Soldermask,Top*",
    ],
)
def test_present_but_unusable_x2_does_not_fall_back_to_filename(attribute: str) -> None:
    assert infer_layer("top.gtl", attribute) is None


def test_filename_fallback_remains_when_x2_is_absent() -> None:
    assert infer_layer("top.gtl", "") == "F.Cu"
