from photonx_eda_pcb.undo_redo.model import Change
def edit_to_change(op):return Change(f"{op.kind}:{op.object_id}",op.before,op.after,op.reason or op.kind)
