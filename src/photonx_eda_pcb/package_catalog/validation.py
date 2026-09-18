def validate_package(e):
    issues=[]
    if not e.name:issues.append("PACKAGE_NAME_EMPTY")
    if e.pin_count<=0:issues.append("PACKAGE_PIN_COUNT")
    for v in (e.pitch_mm,e.body_width_mm,e.body_height_mm):
        if v is not None and v<=0:issues.append("PACKAGE_DIMENSION_NONPOSITIVE")
    return issues
