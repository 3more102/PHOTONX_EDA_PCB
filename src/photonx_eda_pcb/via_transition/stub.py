def stub_penalty(stub_layers,total_layers):
    if total_layers<=0:return 0.0
    return round(min(1.0,max(0,int(stub_layers))/int(total_layers)),6)
