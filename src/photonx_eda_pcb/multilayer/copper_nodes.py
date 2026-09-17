def copper_node(object_id,layer): return f"{object_id}@{layer}"
def split_node(node): return tuple(str(node).rsplit("@",1))
