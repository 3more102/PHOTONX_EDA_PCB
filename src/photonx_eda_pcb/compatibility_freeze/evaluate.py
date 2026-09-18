def evaluate_compatibility_freeze(matrix,migrations,allowed_status=("implemented","supported","experimental")):
    from .model import CompatibilityFreezeDecision
    blockers=[];warnings=[];allowed=set(allowed_status)
    for e in matrix.entries:
        status=str(e.status).lower()
        if status in {"unsupported","broken","failed"}:blockers.append(f"COMPATIBILITY_{e.feature}_{e.format}_{status}".upper())
        elif status not in allowed:warnings.append(f"COMPATIBILITY_{e.feature}_{status}".upper())
        if status in {"implemented","supported"} and not e.tests:warnings.append(f"COMPATIBILITY_TESTS_MISSING_{e.feature}".upper())
    plans=list(migrations)
    for p in plans:
        if p.status in {"active","proposed"} and any(s.breaking for s in p.steps):blockers.append("BREAKING_MIGRATION_OPEN_"+p.id)
        elif p.status=="active":warnings.append("MIGRATION_ACTIVE_"+p.id)
    return CompatibilityFreezeDecision(not blockers,tuple(sorted(set(blockers))),tuple(sorted(set(warnings))),len(matrix.entries),len(plans))
