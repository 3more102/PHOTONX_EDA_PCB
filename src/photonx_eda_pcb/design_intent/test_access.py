def test_access_score(net_degrees,testpoint_nets):
    tp=set(testpoint_nets)
    return {n:round((1.0 if n in tp else 0.0)+min(float(d),5.0)*0.05,3) for n,d in net_degrees.items()}
