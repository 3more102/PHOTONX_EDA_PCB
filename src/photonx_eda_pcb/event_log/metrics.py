from collections import Counter
def event_metrics(log):
    c=Counter(e.kind for e in log.all());return {"count":len(log),"kinds":dict(sorted(c.items()))}
