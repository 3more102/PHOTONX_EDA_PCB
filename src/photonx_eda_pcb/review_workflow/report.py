def queue_summary(queue):
    out={"total":len(queue.items)}
    for x in queue.items:out[x.status]=out.get(x.status,0)+1
    return out
