from photonx_eda_pcb.reference_designators.assign import assign_missing_references
class C:
    def __init__(self,id,kind,reference=None):self.id=id;self.kind=kind;self.reference=reference
def test_assign_missing_references_deterministic():
    out=assign_missing_references([C("b","resistor"),C("a","capacitor"),C("c","resistor")],used=["R1"])
    assert out=={"a":"C1","b":"R2","c":"R3"}
