def evidence_confidence(has_width=True,has_stack_height=False,has_er=False,has_plane_reference=False):
    score=(0.2 if has_width else 0)+(0.3 if has_stack_height else 0)+(0.3 if has_er else 0)+(0.2 if has_plane_reference else 0)
    return round(min(score,1.0),12)
