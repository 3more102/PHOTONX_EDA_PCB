def validate_document(doc):
    issues=[]
    for pid,p in doc.pages.items():
        for oid in p.symbol_ids:
            if oid not in doc.symbols:issues.append("EDITOR_PAGE_UNKNOWN_SYMBOL")
        for oid in p.wire_ids:
            if oid not in doc.wires:issues.append("EDITOR_PAGE_UNKNOWN_WIRE")
        for oid in p.label_ids:
            if oid not in doc.labels:issues.append("EDITOR_PAGE_UNKNOWN_LABEL")
        for oid in p.bus_ids:
            if oid not in doc.buses:issues.append("EDITOR_PAGE_UNKNOWN_BUS")
    for s in doc.symbols.values():
        if s.page_id not in doc.pages:issues.append("EDITOR_SYMBOL_UNKNOWN_PAGE")
        if not 0<=s.confidence<=1:issues.append("EDITOR_SYMBOL_CONFIDENCE_RANGE")
    for w in doc.wires.values():
        if len(w.points)<2:issues.append("EDITOR_WIRE_TOO_SHORT")
    return issues
