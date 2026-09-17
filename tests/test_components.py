from pathlib import Path
from photonx_eda_pcb import reconstruct
FIX=Path(__file__).parent/"fixtures"/"led"

def test_components_are_hypotheses_not_fake_bom():
    comps=reconstruct(FIX).board.components; assert len(comps)==3; assert all(c.reference is None for c in comps); assert all(c.kind.endswith("candidate") for c in comps); assert all(c.confidence<0.8 for c in comps)
