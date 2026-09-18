def layout_report(layout):return {"width":layout.width,"height":layout.height,"positions":[p.__dict__ for p in sorted(layout.positions.values(),key=lambda x:x.object_id)]}
