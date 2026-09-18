from photonx_eda_pcb.assembly_reconstruction.model import AssemblyComponent
from photonx_eda_pcb.assembly_reconstruction.overlap import close_component_pairs
def test_close_pairs_same_side():
    c=[AssemblyComponent("A",(0,0),0,"top"),AssemblyComponent("B",(.1,0),0,"top"),AssemblyComponent("C",(.1,0),0,"bottom")]
    out=close_component_pairs(c,.2)
    assert len(out)==1 and out[0][0:2]==("A","B")
