from collections import Counter
def collect_issue_counts(*issue_groups):
    c=Counter()
    for group in issue_groups:
        for x in group:c[getattr(x,'severity',x.get('severity','unknown') if isinstance(x,dict) else 'unknown')]+=1
    return dict(c)
def collect_metrics(**values):return {k:v for k,v in sorted(values.items()) if v is not None}
