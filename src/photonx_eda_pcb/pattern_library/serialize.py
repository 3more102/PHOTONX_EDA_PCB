import json
from .model import PatternDefinition
from .library import PatternLibrary
def dumps_library(lib):return json.dumps([{"name":p.name,"required_kinds":list(p.required_kinds),"min_components":p.min_components,"max_components":p.max_components,"required_roles":list(p.required_roles),"description":p.description} for p in lib.all()],sort_keys=True,separators=(",",":"))
def loads_library(text):
    return PatternLibrary([PatternDefinition(str(x["name"]),tuple(map(str,x.get("required_kinds",[]))),int(x.get("min_components",1)),x.get("max_components"),tuple(map(str,x.get("required_roles",[]))),str(x.get("description",""))) for x in json.loads(text)])
