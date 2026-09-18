def graph_equivalent(a,b):
    return set(a.nodes())==set(b.nodes()) and {tuple(sorted(x)) for x in a.edges()}=={tuple(sorted(x)) for x in b.edges()}
def issues_equivalent(a,b):
    key=lambda x:(x.severity,x.code,x.message,tuple(x.object_ids))
    return sorted(map(key,a))==sorted(map(key,b))
