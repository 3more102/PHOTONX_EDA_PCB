def validate_control_points(points):
    points=list(points); issues=[]
    if len(points)<3: issues.append(("error","ALIGNMENT_TOO_FEW_POINTS",len(points)))
    image_pairs={(p.image_x,p.image_y) for p in points}; board_pairs={(p.board_x,p.board_y) for p in points}
    if len(image_pairs)!=len(points): issues.append(("error","ALIGNMENT_DUPLICATE_IMAGE_POINT"))
    if len(board_pairs)!=len(points): issues.append(("error","ALIGNMENT_DUPLICATE_BOARD_POINT"))
    return issues
