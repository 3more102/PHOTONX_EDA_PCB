from collections import Counter
def duplicates(values): return sorted(k for k,v in Counter(values).items() if v>1)
def unique_preserve_order(values): return list(dict.fromkeys(values))
