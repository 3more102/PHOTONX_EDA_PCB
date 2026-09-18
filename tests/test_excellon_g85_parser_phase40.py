from pathlib import Path
from photonx_eda_pcb.parsers.excellon import ExcellonParser

def test_canonical_g85_slot_parses(tmp_path:Path):
    p=tmp_path/"slot.drl"
    p.write_text("M48\nMETRIC\nT01C0.800\n%\nT01\nX1.000Y2.000G85X3.000Y2.000\nM30\n")
    r=ExcellonParser().parse(p)
    assert len(r.drills)==0 and len(r.slots)==1
    s=r.slots[0]
    assert s.start==(1.0,2.0) and s.end==(3.0,2.0)
    assert s.width_mm==.8 and s.tool=="T01" and s.plated=="unknown"
    assert s.provenance.sources[0].line==6
