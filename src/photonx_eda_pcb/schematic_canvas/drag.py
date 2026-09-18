from photonx_eda_pcb.schematic_canvas.grid import snap_point
def drag_symbol(doc,symbol_id,world_point,grid=2.54):
    from photonx_eda_pcb.schematic_editor.operations import move_symbol
    x,y=snap_point(world_point,grid);return move_symbol(doc,symbol_id,x,y)
