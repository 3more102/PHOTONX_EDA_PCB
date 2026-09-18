from .model import DocumentTab
def open_tab(state,id,title,path=""):
    if not any(t.id==id for t in state.tabs):state.tabs.append(DocumentTab(str(id),str(title),str(path),False))
    state.active_tab=str(id);return state
def close_tab(state,id):
    state.tabs=[t for t in state.tabs if t.id!=str(id)]
    if state.active_tab==str(id):state.active_tab=state.tabs[-1].id if state.tabs else None
    return state
def mark_tab_dirty(state,id,value=True):
    for t in state.tabs:
        if t.id==str(id):t.dirty=bool(value)
    return state
