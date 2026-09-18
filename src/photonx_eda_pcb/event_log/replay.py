def replay(events,handlers,state=None):
    state={} if state is None else state
    for e in sorted(events,key=lambda x:x.seq):
        fn=handlers.get(e.kind)
        if fn is not None:fn(state,e)
    return state
