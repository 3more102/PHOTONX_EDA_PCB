from .base import RuleIssue
def valid_component_references(board):
    pads={p.id for p in getattr(board,'pads',[])}; out=[]
    for c in getattr(board,'components',[]):
        if not 0<=c.confidence<=1: out.append(RuleIssue('error','COMPONENT_CONFIDENCE','component confidence outside [0,1]',c.id))
        for pid in c.pad_ids:
            if pid not in pads: out.append(RuleIssue('error','COMPONENT_PAD_MISSING',f'unknown pad {pid}',c.id))
    return out
