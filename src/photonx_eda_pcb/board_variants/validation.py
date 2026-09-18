def validate_variant(v):
    issues=[]
    if not v.name.strip():issues.append("VARIANT_NAME_EMPTY")
    for ref,x in v.components.items():
        if ref!=x.reference:issues.append("VARIANT_REFERENCE_KEY_MISMATCH")
        if not ref.strip():issues.append("VARIANT_REFERENCE_EMPTY")
    return issues
