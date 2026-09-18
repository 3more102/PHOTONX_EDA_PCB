def enqueue(queue,item):
    if any(x.id==item.id for x in queue.items):raise ValueError("duplicate review id")
    queue.items.append(item);return queue
def next_item(queue):
    open_items=[x for x in queue.items if x.status=="open"]
    return sorted(open_items,key=lambda x:(-x.priority,x.id))[0] if open_items else None
