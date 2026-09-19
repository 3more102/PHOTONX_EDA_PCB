def validate_diff(diff):
    issues = []
    seen_entries = set()
    seen_object_ids = set()

    for entry in diff.entries:
        key = (entry.kind, entry.object_id)
        if key in seen_entries:
            issues.append("DIFF_DUPLICATE_ENTRY")
        seen_entries.add(key)

        if entry.object_id in seen_object_ids:
            issues.append("DIFF_OBJECT_ID_REPEATED")
        seen_object_ids.add(entry.object_id)

        if entry.kind not in {"added", "removed", "changed"}:
            issues.append("DIFF_KIND_UNKNOWN")
            continue

        if entry.kind == "added" and (entry.before is not None or entry.after is None):
            issues.append("DIFF_PAYLOAD_INVALID")
        elif entry.kind == "removed" and (entry.before is None or entry.after is not None):
            issues.append("DIFF_PAYLOAD_INVALID")
        elif entry.kind == "changed" and (entry.before is None or entry.after is None):
            issues.append("DIFF_PAYLOAD_INVALID")

    return issues
