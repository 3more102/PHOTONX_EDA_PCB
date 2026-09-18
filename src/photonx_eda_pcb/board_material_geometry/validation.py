def validate_material_shape(shape):
    if shape is None:return ["BOARD_MATERIAL_UNAVAILABLE"]
    issues=[]
    if shape.is_empty:issues.append("BOARD_MATERIAL_EMPTY")
    if not shape.is_valid:issues.append("BOARD_MATERIAL_INVALID")
    if shape.area<=0:issues.append("BOARD_MATERIAL_ZERO_AREA")
    return issues
