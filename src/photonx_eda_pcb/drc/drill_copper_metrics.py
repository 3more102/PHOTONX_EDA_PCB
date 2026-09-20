def drill_copper_metrics(board,cfg):
    from .drill_copper import check_drill_copper_clearance
    issues=check_drill_copper_clearance(board,cfg)
    copper_objects=len(board.tracks)+len(board.pads)+len(getattr(board,"regions",()))
    return {"drills":len(board.drills),"copper_objects":copper_objects,"violations":len(issues)}
