def invalidate_tree(cache,index,key):
    removed=[]
    for k in [str(key),*index.descendants(key)]:
        if cache.invalidate(k) is not None:removed.append(k)
    return removed
