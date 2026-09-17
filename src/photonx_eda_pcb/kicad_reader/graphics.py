from .query import children,child
def read_edge_lines(root):
    out=[]
    for g in children(root,'gr_line'):
        layer=child(g,'layer')
        if layer and str(layer[1])=='Edge.Cuts':
            s=child(g,'start'); e=child(g,'end'); out.append(((float(s[1]),float(s[2])),(float(e[1]),float(e[2]))))
    return out
