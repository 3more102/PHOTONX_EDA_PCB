def field_value(item,path):
    cur=item
    for part in str(path).split("."):
        if isinstance(cur,dict):cur=cur.get(part)
        else:cur=getattr(cur,part,None)
        if cur is None:break
    return cur
