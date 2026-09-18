from photonx_eda_pcb.query_engine import parse_query,execute_query
from photonx_eda_pcb.query_engine.sort import sort_items
def apply_preset(items,preset):
    out=execute_query(items,parse_query(preset.query))
    if preset.sort_field:out=sort_items(out,preset.sort_field,preset.reverse)
    return out
