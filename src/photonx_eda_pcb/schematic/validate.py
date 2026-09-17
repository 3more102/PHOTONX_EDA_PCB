def validate_schematic_hypotheses(items):
    issues=[]
    for x in items:
        if x.get('status')!='hypothesis':issues.append(('warning','SCHEMATIC_STATUS',x.get('component_id')))
        if not 0<=x.get('confidence',0)<=1:issues.append(('error','SCHEMATIC_CONFIDENCE',x.get('component_id')))
    return issues
