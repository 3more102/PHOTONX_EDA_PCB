def netclass_for_net(classes,net_id):
    return next((c for c in classes if str(net_id) in c.nets),None)
