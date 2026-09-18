DEFAULT_CONSTRAINTS={"signal":{"min_width_mm":0.15,"clearance_mm":0.15},"power":{"min_width_mm":0.3,"clearance_mm":0.2},"ground":{"min_width_mm":0.2,"clearance_mm":0.15},"differential":{"min_width_mm":0.15,"clearance_mm":0.15}}
def constraints_for(candidate):
    return dict(DEFAULT_CONSTRAINTS.get(candidate.class_name,DEFAULT_CONSTRAINTS["signal"]))
