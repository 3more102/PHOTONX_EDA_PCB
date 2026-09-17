from photonx_eda_pcb.models import *
from photonx_eda_pcb.schematic.netlist import component_net_map
from photonx_eda_pcb.schematic.export import export_connectivity_text

def test_component_net_map():
 p=PadCandidate('p',Point(0,0),1,1,'C','F.Cu'); n=NetGroup('N1',['p'],.8); c=ComponentHypothesis('C1',['p'],'TWO_PIN_THT',.6,[]); b=BoardModel(pads=[p],nets=[n],components=[c]); assert component_net_map(b)['C1']==['N1']; assert 'physical connectivity' in export_connectivity_text(b)
