ROLE_IMPACT={"gerber_copper":{"geometry","connectivity","nets"},"gerber_outline":{"outline","board_bounds"},"excellon":{"drills","vias","connectivity"},"ipc356":{"net_labels","electrical_evidence"},"bom":{"component_identity","values"},"pick_place":{"assembly","placement"}}
def impacted_domains(change):
    roles=set()
    if change.before:roles.add(change.before.role)
    if change.after:roles.add(change.after.role)
    out=set()
    for r in roles:out|=ROLE_IMPACT.get(r,{"import"})
    return sorted(out)
