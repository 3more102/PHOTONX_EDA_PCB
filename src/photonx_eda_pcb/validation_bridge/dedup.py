def deduplicate_issues(items):
    seen=set();out=[]
    for x in items:
        key=(x.source,x.code,x.severity,x.message,x.object_id)
        if key not in seen:seen.add(key);out.append(x)
    return out
