def push_recent(items,path,limit=10):
    p=str(path);out=[x for x in items if x!=p];out.insert(0,p);return out[:int(limit)]
