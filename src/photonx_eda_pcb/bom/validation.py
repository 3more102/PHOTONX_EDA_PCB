def validate_bom(items):
    issues=[]; seen=set()
    for item in items:
        for reference in item.references:
            if reference in seen: issues.append(("warning","BOM_REFERENCE_DUPLICATE",reference))
            seen.add(reference)
        if item.quantity is not None and item.quantity!=len(item.references): issues.append(("info","BOM_QUANTITY_REFERENCE_MISMATCH",item.quantity,len(item.references)))
    return issues
