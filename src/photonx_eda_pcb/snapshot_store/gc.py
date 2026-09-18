def reachable_snapshot_ids(store,roots):
    seen=set();stack=list(roots)
    while stack:
        sid=stack.pop()
        if sid in seen:continue
        seen.add(sid);s=store.get(sid)
        if s.parent_id is not None:stack.append(s.parent_id)
    return seen
