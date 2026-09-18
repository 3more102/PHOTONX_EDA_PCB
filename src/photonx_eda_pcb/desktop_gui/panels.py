def show_panel(state,id):
    if id in state.panels:state.panels[id].visible=True
    return state
def hide_panel(state,id):
    if id in state.panels:state.panels[id].visible=False
    return state
def toggle_panel(state,id):
    if id in state.panels:state.panels[id].visible=not state.panels[id].visible
    return state
