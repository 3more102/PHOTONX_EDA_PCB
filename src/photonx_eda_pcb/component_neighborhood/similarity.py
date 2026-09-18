def neighborhood_similarity(a,b):
    na=set(a.neighbors);nb=set(b.neighbors);nn=set(a.nets);bn=set(b.nets)
    neigh=1.0 if not na and not nb else len(na&nb)/max(1,len(na|nb))
    nets=1.0 if not nn and not bn else len(nn&bn)/max(1,len(nn|bn))
    return round(.6*neigh+.4*nets,6)
