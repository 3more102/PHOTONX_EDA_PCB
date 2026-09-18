def stress_report(name,board,connectivity_metrics=None,drc_metrics=None):
    from .metrics import board_size_metrics
    out={"name":str(name),"board":board_size_metrics(board)}
    if connectivity_metrics is not None:out["connectivity"]=dict(connectivity_metrics)
    if drc_metrics is not None:out["drc"]=dict(drc_metrics)
    return out
