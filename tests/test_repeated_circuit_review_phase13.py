from photonx_eda_pcb.repeated_circuits.model import CircuitInstance,RepeatedCircuitGroup
from photonx_eda_pcb.repeated_circuits.review import review_items
def test_ambiguous_repeat_enters_review():
    inst=(CircuitInstance("i1","A",("A",),(),"x",.8,("semantics",)),CircuitInstance("i2","B",("B",),(),"y",.8,()))
    g=RepeatedCircuitGroup("g",inst,"t",.8,.7,())
    assert review_items([g])
