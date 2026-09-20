_REASON_CODES={
    "skipped_outline":{
        "KICAD_OUTLINE_COORDINATE_INVALID",
        "KICAD_OUTLINE_ZERO_LENGTH",
    },
    "skipped_drills":{
        "KICAD_DRILL_PLATING_UNKNOWN",
        "KICAD_DRILL_PLATED_PADSTACK_UNSUPPORTED",
        "KICAD_DRILL_GEOMETRY_INVALID",
        "KICAD_DRILL_PLATING_UNSUPPORTED",
    },
    "skipped_pads":{
        "KICAD_PAD_LAYER_UNSUPPORTED",
        "KICAD_PAD_SHAPE_UNSUPPORTED",
        "KICAD_PAD_DRILL_PADSTACK_UNPROVEN",
    },
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
        "KICAD_TRACK_LAYER_UNSUPPORTED",
    },
    "omitted_routes":{
        "KICAD_ARBITRARY_ROUTE_UNSUPPORTED",
    },
    "omitted_via_spans":{
        "KICAD_PROVEN_VIA_SPAN_UNSUPPORTED",
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
    exported_drills=list(data.get("exported_drills",()))
    exported_outline=list(data.get("exported_outline",()))
    skipped_outline=list(data.get("skipped_outline",()))
    skipped_drills=list(data.get("skipped_drills",()))
    exported_pads=list(data.get("exported_pads",()))
    skipped_pads=list(data.get("skipped_pads",()))
    skipped_slots=list(data.get("skipped_slots",()))
    exported_regions=list(data.get("exported_regions",()))
    skipped_regions=list(data.get("skipped_regions",()))
    exported_tracks=list(data.get("exported_tracks",()))
    skipped_tracks=list(data.get("skipped_tracks",()))
    omitted_routes=list(data.get("omitted_routes",()))
    omitted_via_spans=list(data.get("omitted_via_spans",()))

    duplicate_checks=(
        ("OMISSION_EXPORTED_SLOT_DUPLICATE_ID",exported_slots),
        ("OMISSION_EXPORTED_DRILL_DUPLICATE_ID",exported_drills),
        ("OMISSION_EXPORTED_OUTLINE_DUPLICATE_ID",exported_outline),
        ("OMISSION_SKIPPED_OUTLINE_DUPLICATE_ID",skipped_outline),
        ("OMISSION_SKIPPED_DRILL_DUPLICATE_ID",skipped_drills),
        ("OMISSION_EXPORTED_PAD_DUPLICATE_ID",exported_pads),
        ("OMISSION_SKIPPED_PAD_DUPLICATE_ID",skipped_pads),
        ("OMISSION_SKIPPED_SLOT_DUPLICATE_ID",skipped_slots),
        ("OMISSION_EXPORTED_REGION_DUPLICATE_ID",exported_regions),
        ("OMISSION_SKIPPED_REGION_DUPLICATE_ID",skipped_regions),
        ("OMISSION_EXPORTED_TRACK_DUPLICATE_ID",exported_tracks),
        ("OMISSION_SKIPPED_TRACK_DUPLICATE_ID",skipped_tracks),
        ("OMISSION_ROUTE_DUPLICATE_ID",omitted_routes),
        ("OMISSION_VIA_SPAN_DUPLICATE_ID",omitted_via_spans),
    )
    for code,values in duplicate_checks:
        if _duplicate(values):issues.append(code)

    overlap_checks=(
        ("OMISSION_SLOT_BOTH_EXPORTED_AND_SKIPPED",exported_slots,skipped_slots),
        ("OMISSION_DRILL_BOTH_EXPORTED_AND_SKIPPED",exported_drills,skipped_drills),
        ("OMISSION_OUTLINE_BOTH_EXPORTED_AND_SKIPPED",exported_outline,skipped_outline),
        ("OMISSION_PAD_BOTH_EXPORTED_AND_SKIPPED",exported_pads,skipped_pads),
        ("OMISSION_REGION_BOTH_EXPORTED_AND_SKIPPED",exported_regions,skipped_regions),
        ("OMISSION_TRACK_BOTH_EXPORTED_AND_SKIPPED",exported_tracks,skipped_tracks),
    )
    for code,exported,skipped in overlap_checks:
        if set(exported)&set(skipped):issues.append(code)

    manifest_issues=list(data.get("issues",()))
    reason_checks=(
        ("OMISSION_SKIPPED_SLOT_WITHOUT_REASON","skipped_slots",skipped_slots),
        ("OMISSION_SKIPPED_DRILL_WITHOUT_REASON","skipped_drills",skipped_drills),
        ("OMISSION_SKIPPED_OUTLINE_WITHOUT_REASON","skipped_outline",skipped_outline),
        ("OMISSION_SKIPPED_PAD_WITHOUT_REASON","skipped_pads",skipped_pads),
        ("OMISSION_SKIPPED_REGION_WITHOUT_REASON","skipped_regions",skipped_regions),
        ("OMISSION_SKIPPED_TRACK_WITHOUT_REASON","skipped_tracks",skipped_tracks),
        ("OMISSION_ROUTE_WITHOUT_REASON","omitted_routes",omitted_routes),
        ("OMISSION_VIA_SPAN_WITHOUT_REASON","omitted_via_spans",omitted_via_spans),
    )
    for code,key,values in reason_checks:
        if _missing_reason(values,manifest_issues,_REASON_CODES[key]):issues.append(code)
    return issues
