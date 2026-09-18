def topological_order(stages):
    by={s.name:s for s in stages};done=set();temp=set();out=[]
    def visit(name):
        if name in done:return
        if name in temp:raise ValueError("stage dependency cycle")
        if name not in by:raise KeyError(name)
        temp.add(name)
        for dep in by[name].dependencies:visit(dep)
        temp.remove(name);done.add(name);out.append(by[name])
    for s in stages:visit(s.name)
    return out
