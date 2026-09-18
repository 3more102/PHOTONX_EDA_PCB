from .metrics import channel_metrics
def channel_report(r):return {"metrics":channel_metrics(r),"deltas":[x.__dict__ for x in r.deltas]}
