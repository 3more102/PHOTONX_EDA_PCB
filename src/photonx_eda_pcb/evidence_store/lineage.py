from collections import defaultdict
def lineage_map(records):
    out=defaultdict(set)
    for record in records:
        if record.object_id is not None: out[record.object_id].add(record.source)
    return {key:tuple(sorted(value)) for key,value in sorted(out.items())}
