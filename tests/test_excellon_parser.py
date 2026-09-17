from pathlib import Path
from photonx_eda_pcb.parsers.excellon import ExcellonParser
FIX=Path(__file__).parent/"fixtures"/"led"

def test_excellon_extracts_six_drill_hits():
    result=ExcellonParser().parse(FIX/"drill.drl"); assert len(result.drills)==6; assert {d.tool for d in result.drills}=={"T01"}; assert all(d.plating=="unknown" for d in result.drills)
