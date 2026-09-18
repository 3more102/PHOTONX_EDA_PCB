from photonx_eda_pcb.bom_reconciliation import BomRecord,reconcile_bom
from photonx_eda_pcb.assembly_reconstruction.model import AssemblyComponent
def test_bom_reconciliation_detects_value_mismatch():
    bom=[BomRecord("R1","10k","R_0603")]
    comps=[AssemblyComponent("R1",(0,0),0,"top","R_0603","1k",1)]
    issues=reconcile_bom(bom,comps)
    assert [x.code for x in issues]==["VALUE_MISMATCH"]
