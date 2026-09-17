def same_copper_layer(a,b):return getattr(a,'layer',None)==getattr(b,'layer',None)
def vertical_connection_allowed(obj):return getattr(obj,'plating',None)=='plated' or bool(getattr(obj,'span_proven',False))
def may_contact(a,b):
    if same_copper_layer(a,b):return True
    return vertical_connection_allowed(a) or vertical_connection_allowed(b)
