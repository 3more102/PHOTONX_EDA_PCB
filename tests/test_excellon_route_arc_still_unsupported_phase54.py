import pytest
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.errors import UnsupportedFeatureError
def test_route_arc_remains_explicitly_unsupported(tmp_path):
    p=tmp_path/"a.drl";p.write_text("M48\nMETRIC\nT01C0.8\n%\nT01\nG00X1Y1\nM15\nG02X2Y2I1J0\n")
    with pytest.raises(UnsupportedFeatureError):ExcellonParser().parse(p)
