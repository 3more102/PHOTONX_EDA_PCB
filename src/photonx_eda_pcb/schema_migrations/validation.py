def validate_migration_path(start,target,registry):
    issues=[];v=int(start);seen=set()
    while v<int(target):
        if v in seen:return ["MIGRATION_CYCLE"]
        seen.add(v);m=registry.next_from(v)
        if m is None:return [f"MIGRATION_GAP_{v}"]
        v=m.to_version
    if v!=int(target):issues.append("MIGRATION_OVERSHOOT")
    return issues
