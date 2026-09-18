def align_group(layout,component_ids,axis="y",spacing=20.0):
    ids=[str(x) for x in component_ids if str(x) in layout.positions]
    for i,cid in enumerate(sorted(ids)):
        p=layout.positions[cid]
        from .model import LayoutPosition
        if axis=="y":layout.positions[cid]=LayoutPosition(cid,p.x,i*float(spacing),p.layer)
        else:layout.positions[cid]=LayoutPosition(cid,i*float(spacing),p.y,p.layer)
    return layout
