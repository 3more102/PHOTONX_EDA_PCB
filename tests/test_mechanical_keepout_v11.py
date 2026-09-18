from photonx_eda_pcb.mechanical_keepout import KeepoutRegion,check_keepouts,validate_keepout
class O:
    def __init__(self,id,center):self.id=id;self.center=center
def test_keepout_violation():
    k=KeepoutRegion("K1",(0,0,2,2),"component")
    v=check_keepouts([O("U1",(1,1)),O("R1",(3,3))],[k])
    assert len(v)==1 and v[0].object_id=="U1"
    assert validate_keepout(k)==[]
