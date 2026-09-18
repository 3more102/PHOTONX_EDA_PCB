def group_differences(group):
    return {x.id:list(x.differences) for x in group.instances if x.differences}
def instance_component_delta(a,b):
    sa,sb=set(a.components),set(b.components)
    return {"only_a":tuple(sorted(sa-sb)),"only_b":tuple(sorted(sb-sa))}
