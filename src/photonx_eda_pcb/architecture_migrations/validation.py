def validate_migration_plan(p):
    issues=[];ids=set()
    if not p.id.strip():issues.append("MIGRATION_ID_EMPTY")
    for s in p.steps:
        if s.id in ids:issues.append("MIGRATION_DUPLICATE_STEP")
        ids.add(s.id)
        if not s.source_api or not s.target_api:issues.append("MIGRATION_API_EMPTY")
    return issues
