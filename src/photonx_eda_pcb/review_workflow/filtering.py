def filter_items(queue,*,status=None,kind=None,assignee=None):
    return [x for x in queue.items if (status is None or x.status==status) and (kind is None or x.kind==kind) and (assignee is None or x.assignee==assignee)]
