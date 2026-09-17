def search_text(objects,text):
    query=str(text).strip().lower()
    if not query:return list(objects)
    fields=("id","reference","value","net_id","layer")
    return [obj for obj in objects if any(query in str(getattr(obj,field,"")).lower() for field in fields)]
