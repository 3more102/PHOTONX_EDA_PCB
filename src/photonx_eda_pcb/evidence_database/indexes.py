def build_indexes(db):
    by_object={};by_kind={};by_source={}
    for r in db.all():
        by_object.setdefault(r.object_id,[]).append(r.id);by_kind.setdefault(r.kind,[]).append(r.id);by_source.setdefault(r.source,[]).append(r.id)
    return {"object":by_object,"kind":by_kind,"source":by_source}
