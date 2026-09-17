from .canonicalize import canonical_board_dict
def compare_board_models(a,b):
    da,db=canonical_board_dict(a),canonical_board_dict(b); diffs=[]
    for k in sorted(set(da)|set(db)):
        if da.get(k)!=db.get(k):diffs.append({'section':k,'left_count':len(da.get(k,[])),'right_count':len(db.get(k,[]))})
    return diffs
