def layer_index(stackup,name):
    for i,x in enumerate(stackup.ordered()):
        if x.name==name:return i
    return None
def copper_names(stackup): return [x.name for x in stackup.copper_layers()]
def layer_between(stackup,a,b):
    ordered=stackup.ordered(); ia=next((i for i,x in enumerate(ordered) if x.name==a),None); ib=next((i for i,x in enumerate(ordered) if x.name==b),None)
    if ia is None or ib is None:return []
    lo,hi=sorted((ia,ib)); return [x.name for x in ordered[lo+1:hi]]
