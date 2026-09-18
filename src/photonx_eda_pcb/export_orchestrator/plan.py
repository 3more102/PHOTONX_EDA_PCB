def export_plan(requests):
    seen=set();out=[]
    for r in requests:
        if r.id in seen:raise ValueError("duplicate export request id")
        seen.add(r.id);out.append(r)
    return sorted(out,key=lambda x:(x.format,x.id))
