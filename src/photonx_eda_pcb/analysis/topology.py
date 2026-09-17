from ..models import BoardModel
def orphan_pad_ids(board:BoardModel)->list[str]: return [p.id for p in board.pads if p.net_id is None]
def unassigned_track_ids(board:BoardModel)->list[str]: return [t.id for t in board.tracks if t.net_id is None]
def member_to_net(board:BoardModel)->dict[str,str]:
    out={}
    for n in board.nets:
        for m in n.members: out[m]=n.id
    return out
