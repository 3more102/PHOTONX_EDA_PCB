def dict_diff(a,b):
    keys=sorted(set(a)|set(b)); return {k:(a.get(k),b.get(k)) for k in keys if a.get(k)!=b.get(k)}
