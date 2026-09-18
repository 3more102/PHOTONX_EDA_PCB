from .status import VALID_STATUS
def validate_matrix(m):
    issues=[];seen=set()
    for e in m.entries:
        k=(e.feature,e.format)
        if k in seen:issues.append("COMPAT_DUPLICATE_ENTRY")
        seen.add(k)
        if e.status not in VALID_STATUS:issues.append("COMPAT_BAD_STATUS")
    return issues
