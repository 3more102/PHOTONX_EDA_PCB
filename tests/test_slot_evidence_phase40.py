from pathlib import Path
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.mechanical_features.evidence import slot_evidence

def test_slot_evidence_exposes_source(tmp_path:Path):
    p=tmp_path/"s.drl";p.write_text("M48\nMETRIC\nT01C0.8\n%\nT01\nX1Y1G85X2Y1\nM30\n")
    s=ExcellonParser().parse(p).slots[0]
    e=slot_evidence(s)
    assert e["tool"]=="T01" and e["sources"][0]["path"].endswith("s.drl")
