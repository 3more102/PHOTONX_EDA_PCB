def mechanical_clearance_metrics(features,board,minimum_mm=.15):
    from .mechanical_clearance import check_mechanical_features
    issues=check_mechanical_features(features,board,minimum_mm)
    return {"features":len(features),"copper_objects":len(board.tracks)+len(board.pads),"violations":len(issues)}
