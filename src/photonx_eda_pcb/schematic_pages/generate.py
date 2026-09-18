from .model import SchematicPage,SchematicPageSet
def generate_pages(blocks,max_components=30):
    pages=[]
    for b in sorted(blocks,key=lambda x:(x.kind,x.id)):
        comps=list(b.components)
        if not comps:continue
        for index in range(0,len(comps),int(max_components)):
            chunk=tuple(comps[index:index+int(max_components)])
            suffix=index//int(max_components)+1
            pid=f"{b.id}:p{suffix}"
            title=f"{b.kind.title()} {suffix}" if len(comps)>max_components else b.kind.title()
            pages.append(SchematicPage(pid,title,chunk,b.nets,b.kind))
    return SchematicPageSet(pages)
