from .candidate import RepairCandidate
def stale_net_links(board):
    nets={n.id for n in getattr(board,'nets',[])};out=[]
    for o in [*getattr(board,'tracks',[]),*getattr(board,'pads',[])]:
        nid=getattr(o,'net_id',None)
        if nid is not None and nid not in nets:out.append(RepairCandidate('clear_stale_net_link',(o.id,),1.0,f'net {nid} does not exist',True,{'net_id':nid}))
    return out
