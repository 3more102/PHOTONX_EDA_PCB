from .dependencies import reverse_dependencies
def impacted_nodes(dag,changed_nodes):
    rev=reverse_dependencies(dag);seen=set(map(str,changed_nodes));stack=list(seen)
    while stack:
        cur=stack.pop()
        for child in rev.get(cur,set()):
            if child not in seen:seen.add(child);stack.append(child)
    return sorted(seen)
