import json
from .model import SymbolEntry,SymbolPin
from .catalog import SymbolCatalog
def dumps_catalog(c):
    return json.dumps([{"name":e.name,"kind":e.kind,"reference_prefix":e.reference_prefix,"pins":[p.__dict__ for p in e.pins]} for e in c.all()],sort_keys=True,separators=(",",":"))
def loads_catalog(text):
    items=[]
    for x in json.loads(text):items.append(SymbolEntry(x["name"],x["kind"],tuple(SymbolPin(**p) for p in x["pins"]),x.get("reference_prefix","U")))
    return SymbolCatalog(items)
