import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.excellon import ExcellonParser


def test_route_arc_ij_subset_is_now_supported(tmp_path):
    p = tmp_path / "a.drl"
    p.write_text(
        "M48\n"
        "METRIC\n"
        "T01C0.8\n"
        "%\n"
        "T01\n"
        "G00X10000Y0000\n"
        "M15\n"
        "G03X0000Y10000I-10000J0000\n"
        "M16\n"
        "M30\n"
    )

    result = ExcellonParser().parse(p)

    assert len(result.routes) == 1
    assert len(result.routes[0].points) > 2


def test_route_arc_radius_form_remains_explicitly_unsupported(tmp_path):
    p = tmp_path / "a.drl"
    p.write_text(
        "M48\n"
        "METRIC\n"
        "T01C0.8\n"
        "%\n"
        "T01\n"
        "G00X10000Y0000\n"
        "M15\n"
        "G03X0000Y10000A10000\n"
    )

    with pytest.raises(UnsupportedFeatureError):
        ExcellonParser().parse(p)
