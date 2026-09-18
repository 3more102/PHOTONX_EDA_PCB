def mechanical_summary(board):
    slots=list(getattr(board,"slots",()))
    return {"slots":len(slots),"unknown_plating":sum(getattr(x,"plated","unknown")=="unknown" for x in slots),"plated":sum(getattr(x,"plated","unknown")=="plated" for x in slots),"non_plated":sum(getattr(x,"plated","unknown")=="non-plated" for x in slots)}
