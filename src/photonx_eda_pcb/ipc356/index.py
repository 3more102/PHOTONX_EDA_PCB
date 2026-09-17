from collections import defaultdict
def records_by_net(records):
    result=defaultdict(list)
    for record in records:
        if record.net_name: result[record.net_name].append(record)
    return {key:tuple(value) for key,value in sorted(result.items())}
def records_by_reference(records):
    result=defaultdict(list)
    for record in records:
        if record.reference: result[record.reference].append(record)
    return {key:tuple(value) for key,value in sorted(result.items())}
