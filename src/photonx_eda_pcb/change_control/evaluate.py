def evaluate_change_control(eco_set,snapshot_store,event_log,require_changes=False):
    from .model import ChangeControlDecision
    blockers=[];changes=list(eco_set.changes)
    if require_changes and not changes:blockers.append("CHANGE_CONTROL_NO_ECO")
    if any(not x.approved for x in changes):blockers.append("CHANGE_CONTROL_UNAPPROVED_ECO")
    head=snapshot_store.head()
    if head is None:blockers.append("CHANGE_CONTROL_SNAPSHOT_MISSING")
    if len(event_log)==0:blockers.append("CHANGE_CONTROL_EVENT_LOG_EMPTY")
    return ChangeControlDecision(not blockers,tuple(sorted(blockers)),len(changes),None if head is None else head.id,len(event_log))
