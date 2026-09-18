from .model import EcoChange,EcoSet
def eco_from_board_diff(diff,name="ECO"):
    out=[]
    for i,e in enumerate(diff.entries):
        action={"added":"add","removed":"remove","modified":"modify"}.get(e.kind,e.kind)
        out.append(EcoChange(f"eco:{i:04d}",e.kind,str(e.object_id),action,f"{e.kind} {e.object_id}",False))
    return EcoSet(str(name),out,{})
