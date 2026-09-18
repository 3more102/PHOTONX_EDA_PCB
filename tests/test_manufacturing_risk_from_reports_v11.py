from photonx_eda_pcb.assembly_dfm.model import AssemblyFinding,AssemblyDfmReport
from photonx_eda_pcb.manufacturing_risk.from_reports import from_dfm
def test_dfm_to_risk():
    out=from_dfm(AssemblyDfmReport([AssemblyFinding("X","error")]))
    assert out[0].score==.7
