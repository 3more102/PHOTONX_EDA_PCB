from photonx_eda_pcb.repeated_circuits.model import CircuitInstance,RepeatedCircuitGroup
from photonx_eda_pcb.repeated_circuits.evidence import evidence_records
def test_evidence_per_instance():
    inst=(CircuitInstance("i1","R1",("R1",),("N1",),"h",1.0,()),CircuitInstance("i2","R2",("R2",),("N2",),"h",1.0,()))
    g=RepeatedCircuitGroup("g",inst,"t",1,.9,("same_topology_hash",))
    e=evidence_records([g])
    assert len(e)==2 and len({x.id for x in e})==2
