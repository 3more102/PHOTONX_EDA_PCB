from pathlib import Path
from photonx_eda_pcb.parsers.excellon import ExcellonParser
def test_linear_route_sequence(tmp_path:Path):
    p=tmp_path/"r.drl"
    p.write_text("M48\nMETRIC\nT01C0.800\n%\nT01\nG00X1.000Y2.000\nM15\nG01X3.000Y2.000\nG01X3.000Y4.000\nM16\nM30\n")
    r=ExcellonParser().parse(p)
    assert len(r.routes)==1
    q=r.routes[0]
    assert q.points==((1.0,2.0),(3.0,2.0),(3.0,4.0))
    assert q.width_mm==.8 and q.tool=="T01"
