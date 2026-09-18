def constraint_conflicts(a,b,tolerance=1e-9):
    out=[]
    for field in ("min_width_mm","clearance_mm","target_length_mm","length_tolerance_mm","diff_pair_gap_mm"):
        x=getattr(a,field);y=getattr(b,field)
        if x is not None and y is not None and abs(float(x)-float(y))>tolerance:out.append(field)
    return out
