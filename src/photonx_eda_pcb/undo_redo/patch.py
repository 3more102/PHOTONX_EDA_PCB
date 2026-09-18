def apply_change(state,change):
    state[change.key]=change.after;return state
def revert_change(state,change):
    if change.before is None:state.pop(change.key,None)
    else:state[change.key]=change.before
    return state
