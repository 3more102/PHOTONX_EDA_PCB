import json
from .model import VariantDefinition,VariantComponent
def dumps_variant(v):
    return json.dumps({"name":v.name,"components":{r:{"reference":x.reference,"fitted":x.fitted,"value":x.value,"footprint":x.footprint} for r,x in sorted(v.components.items())},"metadata":v.metadata},sort_keys=True,separators=(",",":"))
def loads_variant(text):
    d=json.loads(text);comps={r:VariantComponent(**x) for r,x in d.get("components",{}).items()}
    return VariantDefinition(str(d["name"]),comps,dict(d.get("metadata",{})))
