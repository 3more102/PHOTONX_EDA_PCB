import pytest
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.errors import ParseError
def test_unterminated_route_fails_strict(tmp_path):
    p=tmp_path/"a.drl";p.write_text("M48\nMETRIC\nT01C0.8\n%\nT01\nG00X1Y1\nM15\nG01X2Y2\n")
    with pytest.raises(ParseError):ExcellonParser().parse(p)
def test_unterminated_route_warns_permissive(tmp_path):
    p=tmp_path/"b.drl";p.write_text("M48\nMETRIC\nT01C0.8\n%\nT01\nG00X1Y1\nM15\nG01X2Y2\n")
    r=ExcellonParser(strict=False).parse(p)
    assert any(x.code=="EXCELLON_ROUTE_UNTERMINATED" for x in r.diagnostics)
