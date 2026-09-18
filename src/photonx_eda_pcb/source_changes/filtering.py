def filter_changes(cs,*,change_type=None,role=None):
    out=[]
    for c in cs.changes:
        if change_type is not None and c.change_type!=change_type:continue
        roles={x.role for x in (c.before,c.after) if x is not None}
        if role is not None and role not in roles:continue
        out.append(c)
    return out
