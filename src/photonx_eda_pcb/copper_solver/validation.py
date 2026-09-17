def validate_result(result):
    issues=[];seen=set()
    for g in result.groups:
        for x in g:
            if x in seen:issues.append({'severity':'error','code':'SOLVER_OBJECT_DUPLICATED','object':x})
            seen.add(x)
    for e in result.edges:
        if e.a not in seen or e.b not in seen:issues.append({'severity':'error','code':'SOLVER_EDGE_UNKNOWN_OBJECT','edge':(e.a,e.b)})
    return issues
