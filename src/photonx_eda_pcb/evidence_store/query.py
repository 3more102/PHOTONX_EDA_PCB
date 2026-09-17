def filter_evidence(records,kind=None,source=None,min_confidence=0.0,object_id=None):
    return [record for record in records if (kind is None or record.kind==kind) and (source is None or record.source==source) and record.confidence>=min_confidence and (object_id is None or record.object_id==object_id)]
