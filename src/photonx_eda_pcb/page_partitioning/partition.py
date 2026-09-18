from .model import PagePartition
def partition_blocks(blocks,max_components=25):
    maxc=max(1,int(max_components));out=[];page=[];count=0;idx=1
    def flush(items,index):
        comps=tuple(sorted({c for b in items for c in b.components}));nets=tuple(sorted({n for b in items for n in b.nets}));kinds=sorted({b.kind for b in items})
        title=(kinds[0].title() if len(kinds)==1 else "Mixed")+" "+str(index)
        return PagePartition(f"page:{index}",title,tuple(b.id for b in items),comps,nets,len(comps))
    for b in sorted(blocks,key=lambda x:(x.kind,x.id)):
        n=len(b.components)
        if page and count+n>maxc:out.append(flush(page,idx));idx+=1;page=[];count=0
        page.append(b);count+=n
    if page:out.append(flush(page,idx))
    return out
