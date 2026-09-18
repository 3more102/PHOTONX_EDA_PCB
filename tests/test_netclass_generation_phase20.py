from photonx_eda_pcb.constraint_synthesis import synthesize_constraints
from photonx_eda_pcb.netclass_generation import generate_netclasses,validate_generated_netclass
def test_generated_netclasses():
    s=synthesize_constraints(["a","b","p"],{"a":("signal",),"b":("signal",),"p":("power",)})
    classes=generate_netclasses(s,{"a":("signal",),"b":("signal",),"p":("power",)})
    assert sum(len(c.nets) for c in classes)==3
    assert any(c.name.startswith("power_") for c in classes)
    assert all(validate_generated_netclass(c)==[] for c in classes)
