from photonx_eda_pcb.validation_pipeline import ValidationCheck,ValidationRegistry,run_validation
from photonx_eda_pcb.validation_pipeline.decision import validation_passed
def test_validation_blocks_error():
    r=ValidationRegistry();r.register(ValidationCheck("bad","error","x"),lambda c:["broken"])
    assert not validation_passed(run_validation(r),"error")
