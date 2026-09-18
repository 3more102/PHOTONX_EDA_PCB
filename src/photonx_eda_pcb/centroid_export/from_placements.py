from .model import CentroidRecord
def from_placements(placements):
    return [CentroidRecord(str(p.reference),float(p.x),float(p.y),float(p.rotation)%360,str(p.side).lower(),str(p.footprint),str(p.value)) for p in sorted(placements,key=lambda x:str(x.reference))]
