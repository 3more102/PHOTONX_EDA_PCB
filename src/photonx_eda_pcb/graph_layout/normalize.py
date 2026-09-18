from .model import LayoutPosition
def normalize_layout(layout,origin=(20.0,20.0),grid=2.54):
    ox,oy=map(float,origin);g=float(grid)
    xs=[p.x for p in layout.positions.values()];ys=[p.y for p in layout.positions.values()]
    minx=min(xs,default=0);miny=min(ys,default=0)
    for cid,p in list(layout.positions.items()):
        x=round(round((p.x-minx+ox)/g)*g,6);y=round(round((p.y-miny+oy)/g)*g,6)
        layout.positions[cid]=LayoutPosition(cid,x,y,p.layer)
    return layout
