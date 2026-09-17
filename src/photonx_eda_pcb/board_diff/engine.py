from .model import DiffEntry,BoardDiff

def _index(items):return {str(getattr(x,'id',i)):x for i,x in enumerate(items)}

def diff_collections(before,after):
    a=_index(before); b=_index(after); out=[]
    for k in sorted(a.keys()-b.keys()):out.append(DiffEntry('removed',k,a[k],None))
    for k in sorted(b.keys()-a.keys()):out.append(DiffEntry('added',k,None,b[k]))
    for k in sorted(a.keys()&b.keys()):
        if a[k]!=b[k]:out.append(DiffEntry('changed',k,a[k],b[k]))
    return BoardDiff(out)
