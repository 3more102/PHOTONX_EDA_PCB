def merge_records(*groups):
    merged={}
    for group in groups:
        for record in group:
            if record.id in merged and merged[record.id]!=record: raise ValueError(f"conflicting evidence record: {record.id}")
            merged[record.id]=record
    return [merged[key] for key in sorted(merged)]
