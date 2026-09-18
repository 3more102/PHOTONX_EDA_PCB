def net_features(net_id,label="",widths=(),is_diff=False,degree=0):
    ws=[float(x) for x in widths]
    return {"net_id":str(net_id),"label":str(label).upper(),"mean_width":sum(ws)/len(ws) if ws else None,"max_width":max(ws) if ws else None,"is_diff":bool(is_diff),"degree":int(degree)}
