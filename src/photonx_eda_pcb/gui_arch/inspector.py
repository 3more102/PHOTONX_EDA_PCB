def inspect_object(board,object_id):
    obj=board.object_index().get(object_id)
    if obj is None:return None
    return dict(vars(obj))
