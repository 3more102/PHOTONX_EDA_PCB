from .model import GroundTruthResult
def compare_case(case):
    mismatches=[]
    keys=sorted(set(case.expected)|set(case.observed))
    for k in keys:
        if k not in case.expected:mismatches.append(f"UNEXPECTED:{k}");continue
        if k not in case.observed:mismatches.append(f"MISSING:{k}");continue
        a,b=case.expected[k],case.observed[k]
        tol=case.tolerances.get(k)
        if tol is not None and isinstance(a,(int,float)) and isinstance(b,(int,float)):
            if abs(float(a)-float(b))>float(tol):mismatches.append(f"MISMATCH:{k}")
        elif a!=b:mismatches.append(f"MISMATCH:{k}")
    return GroundTruthResult(case.id,not mismatches,tuple(mismatches))
