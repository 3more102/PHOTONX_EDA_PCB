from photonx_eda_pcb.pick_place.model import Placement
from photonx_eda_pcb.assembly_reconstruction import build_assembly
from photonx_eda_pcb.centroid_export import from_placements
from photonx_eda_pcb.netclass_inference import infer_net_classes
from photonx_eda_pcb.release_audit import run_release_audit,audit_passed
def test_phase4_flow():
    p=[Placement("J1",0,0,0,"top","Connector",""),Placement("R1",10,0,0,"top","R","330")]
    assert len(build_assembly(p).components)==2
    assert len(from_placements(p))==2
    assert infer_net_classes([{"net_id":"G","label":"GND"}])[0].class_name=="ground"
    assert audit_passed(run_release_audit(tests_passed=True,unsupported_count=0,critical_findings=0,deterministic=True,provenance_complete=True))
