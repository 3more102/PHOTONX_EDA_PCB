from collections import Counter
from .base import RuleIssue
def valid_component_references(board):
    pads={p.id for p in getattr(board,'pads',[])}; out=[]
    components=list(getattr(board,'components',[]))
    component_id_counts=Counter(c.id for c in components)
    for component_id,count in sorted(component_id_counts.items()):
        if count>1: out.append(RuleIssue('error','DUPLICATE_COMPONENT_ID',f'duplicate component hypothesis id {component_id}',component_id))
    for c in components:
        duplicate_pad_ids=sorted(pid for pid,count in Counter(c.pad_ids).items() if count>1)
        if duplicate_pad_ids: out.append(RuleIssue('error','COMPONENT_PAD_DUPLICATE',f'duplicate pad ids {duplicate_pad_ids}',c.id))
        if not 0<=c.confidence<=1: out.append(RuleIssue('error','COMPONENT_CONFIDENCE','component confidence outside [0,1]',c.id))
        for pid in c.pad_ids:
            if pid not in pads: out.append(RuleIssue('error','COMPONENT_PAD_MISSING',f'unknown pad {pid}',c.id))
    return out
