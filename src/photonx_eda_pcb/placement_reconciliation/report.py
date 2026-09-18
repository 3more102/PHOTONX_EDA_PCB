def placement_report(items):
    return [{"reference":x.reference,"distance_mm":x.distance_mm,"rotation_delta_deg":x.rotation_delta_deg,"side_match":x.side_match,"code":x.code} for x in items]
