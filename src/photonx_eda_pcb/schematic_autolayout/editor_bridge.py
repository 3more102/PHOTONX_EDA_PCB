from photonx_eda_pcb.schematic_editor.operations import move_symbol
def apply_to_editor(doc,result,component_index):
    moved=[]
    for cid,(x,y) in result.positions.items():
        sid=component_index.get(cid)
        if sid is not None and sid in doc.symbols:
            move_symbol(doc,sid,x,y);moved.append(sid)
    return moved
