from photonx_eda_pcb.kicad_reader.sexpr import parse_sexpr
from .tree import children,child,atom
def read_schematic_text(text):
    root=parse_sexpr(text)
    if not isinstance(root,list) or not root or root[0]!="kicad_sch":raise ValueError("not a kicad_sch document")
    out={"version":None,"generator":None,"uuid":None,"symbols":[],"wires":[],"labels":[],"global_labels":[]}
    for key in ("version","generator","uuid"):
        n=child(root,key);out[key]=atom(n)
    for s in children(root,"symbol"):
        lib=atom(child(s,"lib_id"));at=child(s,"at");uid=atom(child(s,"uuid"));props={}
        for p in children(s,"property"):
            if len(p)>=3:props[str(p[1])]=str(p[2])
        out["symbols"].append({"lib_id":lib,"x":float(at[1]),"y":float(at[2]),"rotation":float(at[3]) if len(at)>3 else 0.0,"uuid":uid,"reference":props.get("Reference",""),"value":props.get("Value",""),"footprint":props.get("Footprint","")})
    for w in children(root,"wire"):
        pts=child(w,"pts");xy=[x for x in pts[1:] if isinstance(x,list) and x and x[0]=="xy"] if pts else []
        out["wires"].append({"points":tuple((float(x[1]),float(x[2])) for x in xy),"uuid":atom(child(w,"uuid"))})
    for key in ("label","global_label"):
        target="labels" if key=="label" else "global_labels"
        for l in children(root,key):
            at=child(l,"at");out[target].append({"text":str(l[1]),"x":float(at[1]),"y":float(at[2]),"uuid":atom(child(l,"uuid"))})
    return out
