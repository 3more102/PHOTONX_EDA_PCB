from photonx_eda_pcb.validation_pipeline import ValidationCheck,ValidationRegistry,run_validation
from photonx_eda_pcb.validation_pipeline.decision import validation_passed
def test_validation_pipeline():
    r=ValidationRegistry();r.register(ValidationCheck("ok","error","geometry"),lambda c:[]);r.register(ValidationCheck("warn","warning","geometry"),lambda c:["note"])
    out=run_validation(r,groups=["geometry"])
    assert len(out.results)==2 and validation_passed(out,"error")
