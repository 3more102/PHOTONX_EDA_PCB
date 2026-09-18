def untested_nets(net_ids,testpoints):
    covered={str(tp.net_id) for tp in testpoints if getattr(tp,"net_id",None) and tp.exposed}
    return sorted(set(map(str,net_ids))-covered)
