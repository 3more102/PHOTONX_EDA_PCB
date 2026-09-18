def trim_undo(stack,max_items=100):
    excess=max(0,len(stack.undo_stack)-int(max_items))
    if excess:del stack.undo_stack[:excess]
