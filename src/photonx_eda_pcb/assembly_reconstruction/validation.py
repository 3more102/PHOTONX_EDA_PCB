def validate_assembly(assembly):
    issues=[];seen=set()
    for c in assembly.components:
        if c.reference in seen:issues.append("ASSEMBLY_DUPLICATE_REFERENCE")
        seen.add(c.reference)
        if c.side not in {"top","bottom","front","back","f","b"}:issues.append("ASSEMBLY_UNKNOWN_SIDE")
        if not 0<=c.confidence<=1:issues.append("ASSEMBLY_CONFIDENCE_RANGE")
    return issues
