from collections import Counter
def index_stats(index):
    c=Counter(a.role for a in index.artifacts)
    return {"count":len(index.artifacts),"bytes":sum(a.size for a in index.artifacts),"roles":dict(sorted(c.items()))}
