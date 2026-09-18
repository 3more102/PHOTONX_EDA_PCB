def validate_slot(s):
    issues=[]
    if not s.id:issues.append("SLOT_ID_EMPTY")
    if s.width_mm<=0:issues.append("SLOT_WIDTH_NONPOSITIVE")
    if s.start==s.end:issues.append("SLOT_ZERO_LENGTH")
    return issues
def validate_hole(h):
    issues=[]
    if not h.id:issues.append("MECH_HOLE_ID_EMPTY")
    if h.diameter_mm<=0:issues.append("MECH_HOLE_DIAMETER_NONPOSITIVE")
    return issues
