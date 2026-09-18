def plan_recompute(stages,changed):
    by={s.name:s for s in stages};affected=set(map(str,changed));changed_flag=True
    while changed_flag:
        changed_flag=False
        for s in stages:
            if s.name in affected:continue
            if any(d in affected for d in s.dependencies):affected.add(s.name);changed_flag=True
    return [s.name for s in stages if s.name in affected]
