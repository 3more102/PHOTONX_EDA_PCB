_REASON_CODES={
    "skipped_slots":{
        "KICAD_SLOT_PLATED_UNSUPPORTED",
        "KICAD_SLOT_PLATING_UNKNOWN",
    },
    "skipped_regions":{
        "KICAD_COPPER_REGION_HOLES_UNSUPPORTED",
        "KICAD_COPPER_REGION_LAYER_UNSUPPORTED",
        "KICAD_COPPER_REGION_INVALID_GEOMETRY",
        "KICAD_COPPER_REGION_NET_UNRESOLVED",
    },
    "skipped_tracks":{
        "KICAD_NET_REFERENCE_UNRESOLVED",
    },
    "omitted_routes":{
        "KICAD_ARBITRARY_ROUTE_UNSUPPORTED",
    },
}

def _duplicate(values):
    values=list(values)
    return len(values)!=len(set(values))

def _missing_reason(values,manifest_issues,allowed_codes):
    pairs={(item.get("object_id"),item.get("code")) for item in manifest_issues}
    return any(
        not any((object_id,code) in pairs for code in allowed_codes)
        for object_id in values
    )

def validate_omission_manifest(data):
    issues=[]
    exported_slots=list(data.get("exported_slots",()))
    skipped_slots=list(data.get("skipped_slots",()))
    exported_regions=list(data.get("exported_regions",()))
    skipped_regions=list(data.get("skipped_regions",()))
    exported_tracks=list(data.get("exported_tracks",()))
    skipped_tracks=list(data.get("skipped_tracks",()))
    exported_routes=list(data.get("exported_routes",()))
    omitted_routes=list(data.get("omitted_routes",()))

    duplicate_checks=(
        ("OMISSION_EXPORTED_SLOT_DUPLICATE_ID",exported_slots),
        ("OMISSION_SKIPPED_SLOT_DUPLICATE_ID",skipped_slots),
        ("OMISSION_EXPORTED_REGION_DUPLICATE_ID",exported_regions),
        ("OMISSION_SKIPPED_REGION_DUPLICATE_ID",skipped_regions),
        ("OMISSION_EXPORTED_TRACK_DUPLICATE_ID",exported_tracks),
        ("OMISSION_SKIPPED_TRACK_DUPLICATE_ID",skipped_tracks),
        ("OMISSION_EXPORTED_ROUTE_DUPLICATE_ID",exported_routes),
        ("OMISSION_ROUTE_DUPLICATE_ID",omitted_routes),
    )
    for code,values in duplicate_checks:
        if _duplicate(values):issues.append(code)

    overlap_checks=(
        ("OMISSION_SLOT_BOTH_EXPORTED_AND_SKIPPED",exported_slots,skipped_slots),
        ("OMISSION_REGION_BOTH_EXPORTED_AND_SKIPPED",exported_regions,skipped_regions),
        ("OMISSION_TRACK_BOTH_EXPORTED_AND_SKIPPED",exported_tracks,skipped_tracks),
        ("OMISSION_ROUTE_BOTH_EXPORTED_AND_SKIPPED",exported_routes,omitted_routes),
    )
    for code,exported,skipped in overlap_checks:
        if set(exported)&set(skipped):issues.append(code)

    manifest_issues=list(data.get("issues",()))
    reason_checks=(
        ("OMISSION_SKIPPED_SLOT_WITHOUT_REASON","skipped_slots",skipped_slots),
        ("OMISSION_SKIPPED_REGION_WITHOUT_REASON","skipped_regions",skipped_regions),
        ("OMISSION_SKIPPED_TRACK_WITHOUT_REASON","skipped_tracks",skipped_tracks),
        ("OMISSION_ROUTE_WITHOUT_REASON","omitted_routes",omitted_routes),
    )
    for code,key,values in reason_checks:
        if _missing_reason(values,manifest_issues,_REASON_CODES[key]):issues.append(code)
    return issues
