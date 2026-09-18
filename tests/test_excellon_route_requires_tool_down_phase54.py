import pytest
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.errors import ParseError
def test_g01_without_m15_fails(tmp_path):
    p=tmp_path/"a.drl";p.write_text("M48\nMETRIC\nT01C0.8\n%\nT01\nG00X1Y1\nG01X2Y2\n")
    with pytest.raises(ParseError):ExcellonParser().parse(p)
