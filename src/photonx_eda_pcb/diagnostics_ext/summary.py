from collections import Counter
def summarize(records): return dict(sorted(Counter(record.severity for record in records).items()))
