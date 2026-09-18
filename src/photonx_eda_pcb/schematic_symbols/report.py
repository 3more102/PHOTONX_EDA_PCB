def symbol_report(symbols):
    return [{"component":s.component_id,"library_id":s.library_id,"confidence":s.confidence,"pins":len(s.pins)} for s in symbols]
