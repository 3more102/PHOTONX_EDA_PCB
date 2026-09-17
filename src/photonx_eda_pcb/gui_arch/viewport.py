def zoom_by(state,factor,min_zoom=0.05,max_zoom=100.0):
    if factor<=0: raise ValueError('zoom factor must be positive')
    state.zoom=max(min_zoom,min(max_zoom,state.zoom*factor)); return state
def pan_by(state,dx,dy): state.pan_x+=dx; state.pan_y+=dy; return state
