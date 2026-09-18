def conflicting_edits(state):
    by={};out=[]
    for op in state.pending:
        key=(op.kind,op.object_id);by.setdefault(key,[]).append(op)
    for key,ops in by.items():
        values={repr(x.after) for x in ops}
        if len(values)>1:out.append((key,tuple(x.id for x in ops)))
    return out
