from photonx_eda_pcb.pick_place.model import Placement
from photonx_eda_pcb.assembly_reconstruction import build_assembly,validate_assembly
from photonx_eda_pcb.assembly_reconstruction.sides import split_sides
def test_assembly_build_and_split():
    a=build_assembly([Placement("R1",1,2,90,"top","R_0603","10k"),Placement("C1",2,2,0,"bottom","C_0603","100n")])
    top,bottom,other=split_sides(a)
    assert [x.reference for x in top]==["R1"]
    assert [x.reference for x in bottom]==["C1"]
    assert other==[]
    assert validate_assembly(a)==[]
