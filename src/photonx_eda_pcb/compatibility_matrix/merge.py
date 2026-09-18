from .model import CompatibilityMatrix
from .status import status_rank
def merge_matrices(*matrices):
    by={}
    for m in matrices:
        for e in m.entries:
            k=(e.feature,e.format)
            if k not in by or status_rank(e.status)>=status_rank(by[k].status):by[k]=e
    return CompatibilityMatrix([by[k] for k in sorted(by)])
