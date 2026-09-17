def compare_net_labels(physical,semantic):
    out=[]
    for net_id,label in semantic.items():
        if net_id not in physical:out.append({'code':'NET_SOURCE_MISSING_PHYSICAL','net_id':net_id,'label':label})
    return out
