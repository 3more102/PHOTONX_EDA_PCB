def _decide(item,name,note=""):
    item.status="closed";item.decision=name
    if note:item.notes.append(str(note))
    return item
def accept(item,note=""):return _decide(item,"accepted",note)
def reject(item,note=""):return _decide(item,"rejected",note)
def defer(item,note=""):
    item.status="deferred";item.decision="deferred"
    if note:item.notes.append(str(note))
    return item
