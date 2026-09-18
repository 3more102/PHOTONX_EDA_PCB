from .model import ReviewFinding,ReviewReport
def run_manufacturing_review(*,drc_issues=(),erc_issues=(),unresolved=0,unsupported=0):
    f=[]
    for x in drc_issues:f.append(ReviewFinding("DRC","error",str(x)))
    for x in erc_issues:f.append(ReviewFinding("ERC","warning",str(x)))
    if unresolved:f.append(ReviewFinding("UNRESOLVED","warning",f"{unresolved} unresolved reconstruction items"))
    if unsupported:f.append(ReviewFinding("UNSUPPORTED_SYNTAX","critical",f"{unsupported} unsupported input constructs"))
    return ReviewReport(f,{"drc":len(list(drc_issues)),"erc":len(list(erc_issues)),"unresolved":int(unresolved),"unsupported":int(unsupported)})
