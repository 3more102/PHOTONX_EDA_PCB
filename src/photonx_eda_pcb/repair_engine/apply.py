def plan_repairs(candidates,policy):
    approved=[];review=[]
    for c in candidates:
        (approved if policy.permits(c) else review).append(c)
    return {'approved':approved,'review':review}

def apply_repairs(*args,**kwargs):raise RuntimeError('repair application is intentionally disabled; use plan_repairs and human review')
