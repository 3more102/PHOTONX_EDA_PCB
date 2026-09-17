import json
from .model import LayerSpec,StackupModel
def stackup_to_json(s)->str:return json.dumps(s.to_dict(),sort_keys=True,indent=2)+'\n'
def stackup_from_dict(d):return StackupModel([LayerSpec(**x) for x in d.get('layers',[])],float(d.get('confidence',0)),list(d.get('evidence',[])))
