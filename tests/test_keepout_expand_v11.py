from photonx_eda_pcb.mechanical_keepout import KeepoutRegion
from photonx_eda_pcb.mechanical_keepout.expand import expand_keepout
def test_expand_keepout():
    k=expand_keepout(KeepoutRegion("k",(1,1,2,2)),.5)
    assert k.bounds==(.5,.5,2.5,2.5)
