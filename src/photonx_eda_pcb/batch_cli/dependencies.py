def order_jobs(jobs,depends_on):
    by={j.id:j for j in jobs};out=[];temp=set();done=set()
    def visit(jid):
        if jid in done:return
        if jid in temp:raise ValueError("batch dependency cycle")
        temp.add(jid)
        for dep in depends_on.get(jid,()):
            if dep not in by:raise KeyError(dep)
            visit(dep)
        temp.remove(jid);done.add(jid);out.append(by[jid])
    for j in jobs:visit(j.id)
    return out
