def validate_placements(placements):
    issues=[]; seen=set()
    for placement in placements:
        if placement.reference in seen: issues.append(("warning","PNP_REFERENCE_DUPLICATE",placement.reference))
        seen.add(placement.reference)
        if placement.side not in {"top","bottom"}: issues.append(("error","PNP_SIDE_INVALID",placement.reference,placement.side))
    return issues
