def effective_clearance(zone,board_default_mm=0.2):
    return max(float(zone.clearance_mm),float(board_default_mm))

def clearance_violation(distance_mm,zone,board_default_mm=0.2):
    return distance_mm < effective_clearance(zone,board_default_mm)
