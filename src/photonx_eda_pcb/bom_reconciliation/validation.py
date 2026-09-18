from .normalize import normalize_reference
def validate_bom_records(records):
    issues=[];seen=set()
    for r in records:
        ref=normalize_reference(r.reference)
        if not ref:issues.append("BOM_REFERENCE_EMPTY")
        if ref in seen:issues.append("BOM_REFERENCE_DUPLICATE")
        seen.add(ref)
    return issues
