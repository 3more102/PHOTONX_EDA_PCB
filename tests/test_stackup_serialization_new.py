import json
from photonx_eda_pcb.stackup.model import LayerSpec,StackupModel
from photonx_eda_pcb.stackup.serialization import stackup_to_json,stackup_from_dict

def test_stackup_roundtrip():
 s=StackupModel([LayerSpec('F.Cu','top_copper',0,True)],.8,['e']); r=stackup_from_dict(json.loads(stackup_to_json(s))); assert r.layers[0].name=='F.Cu' and r.confidence==.8
