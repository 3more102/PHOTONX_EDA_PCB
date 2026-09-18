def net_test_coverage(net_ids,testpoints):
    nets=set(map(str,net_ids));covered={str(tp.net_id) for tp in testpoints if getattr(tp,"net_id",None)}
    return 1.0 if not nets else round(len(nets&covered)/len(nets),6)
def exposed_testpoint_fraction(testpoints):
    items=list(testpoints)
    return 1.0 if not items else round(sum(bool(tp.exposed) for tp in items)/len(items),6)
