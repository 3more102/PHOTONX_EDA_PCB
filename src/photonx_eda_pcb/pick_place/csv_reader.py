import csv,io
from .model import Placement
from .normalize import header,side
def read_pick_place_csv(text,scale=1.0):
    reader=csv.DictReader(io.StringIO(str(text))); result=[]
    for row in reader:
        data={header(key):value for key,value in row.items() if key is not None}
        ref=data.get("reference") or data.get("ref") or data.get("designator")
        x=data.get("x") or data.get("pos_x") or data.get("center_x"); y=data.get("y") or data.get("pos_y") or data.get("center_y")
        if ref is None or x is None or y is None: continue
        result.append(Placement(ref,float(x)*scale,float(y)*scale,float(data.get("rotation") or data.get("rot") or 0.0),side(data.get("side") or data.get("layer")),data.get("value","") or "",data.get("footprint","") or ""))
    return result
