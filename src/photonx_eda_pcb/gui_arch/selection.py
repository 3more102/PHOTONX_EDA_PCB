def select_object(state,object_id): state.selected_id=object_id; return state
def clear_selection(state): state.selected_id=None; return state
