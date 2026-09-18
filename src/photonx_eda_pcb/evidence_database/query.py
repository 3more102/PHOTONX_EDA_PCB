def query_evidence(db,*,object_id=None,kind=None,source=None,min_confidence=0.0):
    return [r for r in db.all() if (object_id is None or r.object_id==object_id) and (kind is None or r.kind==kind) and (source is None or r.source==source) and r.confidence>=float(min_confidence)]
