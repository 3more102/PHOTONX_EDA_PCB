from .model import BaselineResult
def compare_baseline(baseline,observed):
    diff=[]
    for k,expected in baseline.metrics.items():
        if k not in observed:diff.append(f"MISSING:{k}");continue
        actual=observed[k];tol=baseline.tolerances.get(k)
        if tol is not None and isinstance(expected,(int,float)) and isinstance(actual,(int,float)):
            if abs(float(expected)-float(actual))>float(tol):diff.append(f"MISMATCH:{k}")
        elif expected!=actual:diff.append(f"MISMATCH:{k}")
    for k in observed:
        if k not in baseline.metrics:diff.append(f"NEW:{k}")
    return BaselineResult(baseline.id,not diff,tuple(diff))
