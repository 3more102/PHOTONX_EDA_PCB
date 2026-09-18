from .model import UnifiedIssue
def normalize_issue(issue,source="unknown"):
    if isinstance(issue,UnifiedIssue):return issue
    if isinstance(issue,str):return UnifiedIssue(str(source),issue,"warning",issue,None)
    if isinstance(issue,dict):
        return UnifiedIssue(str(source),str(issue.get("code","UNKNOWN")),str(issue.get("severity","warning")),str(issue.get("message",issue.get("detail",""))),issue.get("object_id"))
    return UnifiedIssue(str(source),str(getattr(issue,"code","UNKNOWN")),str(getattr(issue,"severity","warning")),str(getattr(issue,"message",getattr(issue,"detail",issue))),getattr(issue,"object_id",None))
def normalize_issues(groups):
    out=[]
    for source,items in groups.items():out.extend(normalize_issue(x,source) for x in items)
    return sorted(out,key=lambda x:(x.severity,x.source,x.code,x.object_id or ""))
