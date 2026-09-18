def drill_copper_metrics(board,cfg):
    from .drill_copper import check_drill_copper_clearance
    issues=check_drill_copper_clearance(board,cfg)
    return {"drills":len(board.drills),"copper_objects":len(board.tracks)+len(board.pads),"violations":len(issues)}
