from dataclasses import dataclass,field
from photonx_eda_pcb.fault_injection_engine import Fault,run_fault_suite
from photonx_eda_pcb.fault_injection_engine.metrics import detection_rate
@dataclass
class S: items:list=field(default_factory=lambda:[1,2])
def test_fault_detection_rate():
    faults=[Fault("clear","clear_list","items")]
    r=run_fault_suite(S(),faults,lambda s:["EMPTY"] if not s.items else [])
    assert r[0].detected and detection_rate(r)==1.0
