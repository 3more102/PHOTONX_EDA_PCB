def testpoint_statistics(items):
    return {'count':len(items),'with_net':sum(t.net_id is not None for t in items),'exposed':sum(t.exposed for t in items)}
