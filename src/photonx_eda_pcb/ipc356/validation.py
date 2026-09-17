def validate_records(records):
    issues=[]
    for index,record in enumerate(records):
        if record.record_type=="UNKNOWN": issues.append(("warning","IPC356_RECORD_UNKNOWN",index))
        if record.x is None or record.y is None: issues.append(("info","IPC356_COORDINATE_MISSING",index))
    return issues
