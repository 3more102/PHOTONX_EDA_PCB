from .base import RuleIssue
def valid_net_members(board):
    index=board.object_index() if hasattr(board,'object_index') else {}
    seen={} ; out=[]
    for net in getattr(board,'nets',[]):
        for member in net.members:
            if member not in index: out.append(RuleIssue('error','NET_MEMBER_MISSING',f'{member} does not exist',net.id))
            if member in seen and seen[member]!=net.id: out.append(RuleIssue('error','NET_MEMBER_DUPLICATE',f'{member} belongs to multiple nets',member))
            seen[member]=net.id
    return out
