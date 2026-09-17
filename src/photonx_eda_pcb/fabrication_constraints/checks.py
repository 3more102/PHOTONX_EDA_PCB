def evaluate_constraints(metrics,rules):
    issues=[]
    if metrics.get('min_track_mm',999)<rules.min_track_mm:issues.append('FAB_TRACK_TOO_SMALL')
    if metrics.get('min_clearance_mm',999)<rules.min_clearance_mm:issues.append('FAB_CLEARANCE_TOO_SMALL')
    if metrics.get('min_drill_mm',999)<rules.min_drill_mm:issues.append('FAB_DRILL_TOO_SMALL')
    if metrics.get('min_annular_mm',999)<rules.min_annular_mm:issues.append('FAB_ANNULAR_TOO_SMALL')
    return issues
