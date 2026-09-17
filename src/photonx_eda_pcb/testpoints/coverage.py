def net_coverage(testpoints,net_ids):
    target=set(net_ids); hit={t.net_id for t in testpoints if t.net_id in target}
    return {'nets':len(target),'covered':len(hit),'ratio':(len(hit)/len(target) if target else 1.0)}
