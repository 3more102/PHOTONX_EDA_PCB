from photonx_eda_pcb.current_capacity import estimate_current_capacity,validate_capacity
from photonx_eda_pcb.current_capacity.margin import current_margin
def test_capacity_estimate():
    x=estimate_current_capacity("VCC",1.0,35,10,True,.7)
    assert x.estimated_current_a>0 and validate_capacity(x)==[]
    assert current_margin(x.estimated_current_a,x.estimated_current_a/2)>.4
