from photonx_eda_pcb.models import *
from photonx_eda_pcb.erc import run_erc

def test_erc_unknown_label():
 p=PadCandidate('p',Point(0,0),1,1,'C','F.Cu'); n=NetGroup('N1',['p'],.8); b=BoardModel(pads=[p],nets=[n]); assert any(x.code=='NET_LABEL_UNKNOWN' for x in run_erc(b))
