def normalize_span(a,b,order):
    if a not in order or b not in order: raise ValueError("layer not in stack order")
    ia,ib=order.index(a),order.index(b)
    return (a,b) if ia<=ib else (b,a)
def span_layers(a,b,order):
    lo,hi=normalize_span(a,b,order); i,j=order.index(lo),order.index(hi)
    return tuple(order[i:j+1])
