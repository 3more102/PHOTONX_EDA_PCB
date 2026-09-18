def and_filter(items,*queries):
    from .engine import execute_query
    out=list(items)
    for q in queries:out=execute_query(out,q)
    return out
def or_filter(items,*queries):
    from .engine import execute_query
    out=[];seen=set()
    for q in queries:
        for x in execute_query(items,q):
            k=id(x)
            if k not in seen:seen.add(k);out.append(x)
    return out
