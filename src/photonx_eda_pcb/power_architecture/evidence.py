def architecture_assumptions(a):
    out=[]
    for s in a.stages:
        if not s.input_rails:out.append(f"{s.component_id}:input_rail_unknown")
        if not s.output_rails:out.append(f"{s.component_id}:output_rail_unknown")
    return tuple(out)
