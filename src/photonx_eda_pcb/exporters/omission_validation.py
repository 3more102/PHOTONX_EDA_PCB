def validate_omission_manifest(data):
    issues=[]
    exported=list(data.get("exported_slots",()))
    skipped=list(data.get("skipped_slots",()))
    regions=list(data.get("skipped_regions",()))
    routes=list(data.get("omitted_routes",()))
    if len(exported)!=len(set(exported)):issues.append("OMISSION_EXPORTED_SLOT_DUPLICATE_ID")
    if len(skipped)!=len(set(skipped)):issues.append("OMISSION_SKIPPED_SLOT_DUPLICATE_ID")
    if len(regions)!=len(set(regions)):issues.append("OMISSION_REGION_DUPLICATE_ID")
    if len(routes)!=len(set(routes)):issues.append("OMISSION_ROUTE_DUPLICATE_ID")
    if set(exported)&set(skipped):issues.append("OMISSION_SLOT_BOTH_EXPORTED_AND_SKIPPED")
    manifest_issues=list(data.get("issues",()))
    issue_ids={x.get("object_id") for x in manifest_issues}
    issue_pairs={(x.get("object_id"),x.get("code")) for x in manifest_issues}
    if not set(skipped).issubset(issue_ids):issues.append("OMISSION_SKIPPED_SLOT_WITHOUT_REASON")
    if any((object_id,"KICAD_COPPER_REGION_UNSUPPORTED") not in issue_pairs for object_id in regions):issues.append("OMISSION_REGION_WITHOUT_REASON")
    if any((object_id,"KICAD_ARBITRARY_ROUTE_UNSUPPORTED") not in issue_pairs for object_id in routes):issues.append("OMISSION_ROUTE_WITHOUT_REASON")
    return issues
