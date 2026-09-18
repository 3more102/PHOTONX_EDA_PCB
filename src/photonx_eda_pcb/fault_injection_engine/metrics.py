def detection_rate(results):
    items=list(results);return 1.0 if not items else round(sum(x.detected for x in items)/len(items),6)
