from collections import Counter
def drc_summary(issues): return {'total':len(issues),'by_severity':dict(Counter(x.severity for x in issues)),'by_code':dict(Counter(x.code for x in issues))}
