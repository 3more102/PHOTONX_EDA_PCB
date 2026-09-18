def topology_completeness(t):
    roles={x.role for x in t.lanes};wanted={"data","address","clock"}
    return round(len(roles&wanted)/len(wanted),6)
def lane_counts(t):return {x.role:len(x.nets) for x in t.lanes}
