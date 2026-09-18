def profile_report(p):
    return {"name":p.name,"global":{"min_track_mm":p.min_track_mm,"min_clearance_mm":p.min_clearance_mm,"min_drill_mm":p.min_drill_mm,"min_annular_mm":p.min_annular_mm,"min_mask_sliver_mm":p.min_mask_sliver_mm},"overrides":dict(sorted(p.net_overrides.items()))}
