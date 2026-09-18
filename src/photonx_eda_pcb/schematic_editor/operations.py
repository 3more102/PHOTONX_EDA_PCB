from dataclasses import replace
def _table(doc,obj):
    name=obj.__class__.__name__
    return {"EditorSymbol":doc.symbols,"EditorWire":doc.wires,"EditorLabel":doc.labels,"EditorBus":doc.buses}[name]
def _page_list(page,obj):
    name=obj.__class__.__name__
    return {"EditorSymbol":page.symbol_ids,"EditorWire":page.wire_ids,"EditorLabel":page.label_ids,"EditorBus":page.bus_ids}[name]
def add_object(doc,obj):
    table=_table(doc,obj)
    if obj.id in table:raise ValueError(f"duplicate schematic object {obj.id}")
    if obj.page_id not in doc.pages:raise KeyError(obj.page_id)
    table[obj.id]=obj;_page_list(doc.pages[obj.page_id],obj).append(obj.id);return obj
def remove_object(doc,obj_id):
    for table in (doc.symbols,doc.wires,doc.labels,doc.buses):
        if obj_id in table:
            obj=table.pop(obj_id);lst=_page_list(doc.pages[obj.page_id],obj)
            if obj_id in lst:lst.remove(obj_id)
            return obj
    raise KeyError(obj_id)
def move_symbol(doc,symbol_id,x,y,rotation=None):
    s=doc.symbols[symbol_id];n=replace(s,x=float(x),y=float(y),rotation=s.rotation if rotation is None else float(rotation)%360);doc.symbols[symbol_id]=n;return n
def rename_label(doc,label_id,text):
    x=doc.labels[label_id];n=replace(x,text=str(text));doc.labels[label_id]=n;return n
