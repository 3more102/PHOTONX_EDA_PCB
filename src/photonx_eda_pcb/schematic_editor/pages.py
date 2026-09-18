from .model import EditorPage
def ensure_page(doc,page_id,title=None):
    key=str(page_id)
    if key not in doc.pages:doc.pages[key]=EditorPage(key,str(title or key))
    return doc.pages[key]
def remove_empty_pages(doc,keep=("root",)):
    keep=set(map(str,keep));removed=[]
    for pid in sorted(list(doc.pages)):
        p=doc.pages[pid]
        if pid not in keep and not (p.symbol_ids or p.wire_ids or p.label_ids or p.bus_ids):
            removed.append(pid);del doc.pages[pid]
    return removed
