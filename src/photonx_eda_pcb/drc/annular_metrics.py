from .annular import annular_ring_mm
def annular_metrics(board):
    vals=[(p.id,annular_ring_mm(p)) for p in board.pads if p.drill is not None]
    known=[v for _,v in vals if v is not None]
    return {"drilled_pads":len(vals),"minimum_ring_mm":None if not known else min(known),"broken":sum(v is not None and v<0 for _,v in vals)}
