def query_events(log,*,kind=None,source=None,object_id=None,text=""):
    q=str(text).lower();out=[]
    for e in log.all():
        if kind is not None and e.kind!=kind:continue
        if source is not None and e.source!=source:continue
        if object_id is not None and e.object_id!=object_id:continue
        if q and q not in e.message.lower():continue
        out.append(e)
    return out
