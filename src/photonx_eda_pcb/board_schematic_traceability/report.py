from .coverage import traceability_coverage
def board_schematic_report(t):return {"coverage":traceability_coverage(t),"traces":[{"object_type":x.object_type,"object_id":x.object_id,"page_ids":list(x.page_ids),"net_ids":list(x.net_ids),"component_ids":list(x.component_ids)} for x in t.traces]}
