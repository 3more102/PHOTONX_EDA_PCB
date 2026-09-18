def compare_metrics(expected,observed,tolerances=None):
    tolerances=tolerances or {};diff=[]
    for key in sorted(set(expected)|set(observed)):
        if key not in expected:diff.append(("unexpected",key,None,observed[key]));continue
        if key not in observed:diff.append(("missing",key,expected[key],None));continue
        a,b=expected[key],observed[key];tol=tolerances.get(key)
        if tol is not None and isinstance(a,(int,float)) and isinstance(b,(int,float)):
            if abs(float(a)-float(b))>float(tol):diff.append(("mismatch",key,a,b))
        elif a!=b:diff.append(("mismatch",key,a,b))
    return diff
