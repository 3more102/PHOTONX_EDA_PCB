def canonical_board_dict(board):
    def pt(p):return [round(p.x,6),round(p.y,6)]
    def slot(s):
        return {"id":s.id,"start":[round(float(s.start[0]),6),round(float(s.start[1]),6)],"end":[round(float(s.end[0]),6),round(float(s.end[1]),6)],"width_mm":round(float(s.width_mm),6),"plated":s.plated,"tool":s.tool}
    return {
      "tracks":sorted([{"id":x.id,"start":pt(x.start),"end":pt(x.end),"width":round(x.width,6),"layer":x.layer,"net_id":x.net_id} for x in board.tracks],key=lambda x:x["id"]),
      "pads":sorted([{"id":x.id,"center":pt(x.center),"size":[round(x.size_x,6),round(x.size_y,6)],"shape":x.shape,"layer":x.layer,"drill":x.drill,"net_id":x.net_id} for x in board.pads],key=lambda x:x["id"]),
      "drills":sorted([{"id":x.id,"center":pt(x.center),"diameter":round(x.diameter,6),"plating":x.plating} for x in board.drills],key=lambda x:x["id"]),
      "slots":sorted([slot(x) for x in getattr(board,"slots",())],key=lambda x:x["id"]),
      "regions":sorted([{"id":x.id,"points":[pt(p) for p in x.points],"holes":[[pt(p) for p in ring] for ring in getattr(x,"holes",())],"layer":x.layer,"net_id":x.net_id} for x in getattr(board,"regions",())],key=lambda x:x["id"]),
      "outline":sorted([{"id":x.id,"start":pt(x.start),"end":pt(x.end)} for x in board.outline],key=lambda x:x["id"]),
      "nets":sorted([{"id":x.id,"members":sorted(x.members),"label":x.label} for x in board.nets],key=lambda x:x["id"])
    }
