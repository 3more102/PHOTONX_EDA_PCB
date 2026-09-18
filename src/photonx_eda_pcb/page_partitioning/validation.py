def validate_partitions(parts):
    issues=[];ids=set();components=set()
    for p in parts:
        if p.id in ids:issues.append("PARTITION_DUPLICATE_ID")
        ids.add(p.id)
        overlap=components&set(p.component_ids)
        if overlap:issues.append("PARTITION_COMPONENT_OVERLAP")
        components.update(p.component_ids)
        if p.weight!=len(p.component_ids):issues.append("PARTITION_WEIGHT_MISMATCH")
    return issues
