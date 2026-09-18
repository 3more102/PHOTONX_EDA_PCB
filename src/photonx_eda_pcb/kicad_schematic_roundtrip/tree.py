def children(root,name):return [x for x in root[1:] if isinstance(x,list) and x and x[0]==name]
def child(node,name):
    return next((x for x in node[1:] if isinstance(x,list) and x and x[0]==name),None)
def atom(node,index=1,default=None):
    return node[index] if node is not None and len(node)>index else default
