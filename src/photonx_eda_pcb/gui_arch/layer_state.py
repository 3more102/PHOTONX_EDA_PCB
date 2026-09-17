def set_layer_visible(state,layer,visible=True):
    if visible: state.visible_layers.add(layer)
    else: state.visible_layers.discard(layer)
    return state
def toggle_layer(state,layer): return set_layer_visible(state,layer,layer not in state.visible_layers)
