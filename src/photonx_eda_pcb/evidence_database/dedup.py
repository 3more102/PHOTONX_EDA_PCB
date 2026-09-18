def dedup_key(record):return (record.object_id,record.kind,record.source,record.detail,record.group)
def duplicate_groups(db):
    groups={}
    for r in db.all():groups.setdefault(dedup_key(r),[]).append(r.id)
    return {k:v for k,v in groups.items() if len(v)>1}
