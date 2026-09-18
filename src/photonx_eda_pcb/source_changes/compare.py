from .model import SourceChange,ChangeSet
def compare_sources(before,after):
    a={x.path:x for x in before};b={x.path:x for x in after};out=[]
    for path in sorted(set(a)|set(b)):
        if path not in a:out.append(SourceChange(path,"added",None,b[path]));continue
        if path not in b:out.append(SourceChange(path,"removed",a[path],None));continue
        x,y=a[path],b[path]
        if x.sha256!=y.sha256 or x.size!=y.size or x.role!=y.role:out.append(SourceChange(path,"modified",x,y))
    return ChangeSet(out)
