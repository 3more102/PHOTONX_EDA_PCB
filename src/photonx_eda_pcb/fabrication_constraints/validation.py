def validate_rules(r):
    vals=[r.min_track_mm,r.min_clearance_mm,r.min_drill_mm,r.min_annular_mm]
    return [] if all(v>=0 for v in vals) else ['FAB_RULE_NEGATIVE_VALUE']
