def resolve_profile(profile,net_id=None):
    out={"min_track_mm":profile.min_track_mm,"min_clearance_mm":profile.min_clearance_mm,"min_drill_mm":profile.min_drill_mm,"min_annular_mm":profile.min_annular_mm,"min_mask_sliver_mm":profile.min_mask_sliver_mm}
    if net_id is not None:out.update(profile.net_overrides.get(str(net_id),{}))
    return out
