from .tabs import open_tab
def state_from_session(session,state):
    for path in session.open_documents:open_tab(state,path,path,path)
    if session.active_board:state.active_tab=session.active_board
    return state
