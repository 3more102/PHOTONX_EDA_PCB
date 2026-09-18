import json
def dumps_identities(items):
    return json.dumps([{"component_id":x.component_id,"kind":x.kind,"value":x.value,"footprint":x.footprint,"mpn":x.mpn,"confidence":x.confidence,"sources":list(x.sources),"conflicts":list(x.conflicts)} for x in sorted(items,key=lambda x:x.component_id)],sort_keys=True,separators=(",",":"))
