from collections import defaultdict
def index_by_object(records):
    out=defaultdict(list)
    for record in records:
        if record.object_id is not None: out[record.object_id].append(record)
    return {key:tuple(sorted(value,key=lambda item:item.id)) for key,value in sorted(out.items())}
def index_by_kind(records):
    out=defaultdict(list)
    for record in records: out[record.kind].append(record)
    return {key:tuple(sorted(value,key=lambda item:item.id)) for key,value in sorted(out.items())}
