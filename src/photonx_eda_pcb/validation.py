from __future__ import annotations
from dataclasses import dataclass,field
from .models import BoardModel
from .excellon_routing.validation import validate_route

@dataclass(frozen=True)
class ValidationIssue:
    severity:str
    code:str
    message:str
    object_ids:tuple[str,...]=()

@dataclass
class ValidationReport:
    issues:list[ValidationIssue]=field(default_factory=list)
    @property
    def errors(self):return [i for i in self.issues if i.severity=="error"]
    @property
    def warnings(self):return [i for i in self.issues if i.severity=="warning"]
    @property
    def ok(self):return not self.errors

def validate_board(board:BoardModel,outline_tolerance_mm:float=.05)->ValidationReport:
    r=ValidationReport()
    all_objects=[*board.tracks,*board.pads,*board.drills,*board.outline,*getattr(board,"slots",()),*getattr(board,"routes",())]
    ids=[o.id for o in all_objects]
    if len(ids)!=len(set(ids)):r.issues.append(ValidationIssue("error","DUPLICATE_OBJECT_ID","object IDs must be globally unique"))
    idx=board.object_index();net_members=set()
    for net in board.nets:
        if not 0<=net.confidence<=1:r.issues.append(ValidationIssue("error","INVALID_NET_CONFIDENCE",f"invalid confidence for {net.id}",(net.id,)))
        for member in net.members:
            if member not in idx:r.issues.append(ValidationIssue("error","NET_MEMBER_MISSING",f"{net.id} references missing object {member}",(net.id,member)))
            if member in net_members:r.issues.append(ValidationIssue("error","OBJECT_IN_MULTIPLE_NETS",f"{member} appears in more than one physical net",(member,)))
            net_members.add(member)
    for obj in [*board.tracks,*board.pads]:
        if obj.net_id and obj.id not in net_members:r.issues.append(ValidationIssue("error","OBJECT_NET_BACKREF_MISMATCH",f"{obj.id} has net_id but is not listed in that net",(obj.id,)))
    pad_ids={p.id for p in board.pads}
    for comp in board.components:
        missing=[pid for pid in comp.pad_ids if pid not in pad_ids]
        if missing:r.issues.append(ValidationIssue("error","COMPONENT_PAD_MISSING",f"{comp.id} references missing pads {missing}",(comp.id,*missing)))
        if not 0<=comp.confidence<=1:r.issues.append(ValidationIssue("error","INVALID_COMPONENT_CONFIDENCE",f"invalid confidence for {comp.id}",(comp.id,)))
    for slot in getattr(board,"slots",()):
        if float(slot.width_mm)<=0:r.issues.append(ValidationIssue("error","SLOT_WIDTH_INVALID","slot width must be positive",(slot.id,)))
        if tuple(slot.start)==tuple(slot.end):r.issues.append(ValidationIssue("warning","SLOT_ZERO_LENGTH","slot start and end are identical",(slot.id,)))
        if slot.plated not in {"unknown","plated","non-plated","non_plated"}:r.issues.append(ValidationIssue("warning","SLOT_PLATING_UNKNOWN_ENUM",f"unexpected slot plating value {slot.plated}",(slot.id,)))
    for route in getattr(board,"routes",()):
        for code in validate_route(route):
            sev="warning" if code=="ROUTE_ZERO_LENGTH_SEGMENT" else "error"
            r.issues.append(ValidationIssue(sev,code,code.replace("_"," ").lower(),(route.id,)))
    if board.outline:
        degree={}
        def key(pt):return (round(pt.x/outline_tolerance_mm)*outline_tolerance_mm,round(pt.y/outline_tolerance_mm)*outline_tolerance_mm)
        for seg in board.outline:
            degree[key(seg.start)]=degree.get(key(seg.start),0)+1;degree[key(seg.end)]=degree.get(key(seg.end),0)+1
        bad=[p for p,d in degree.items() if d!=2]
        if bad:r.issues.append(ValidationIssue("warning","OUTLINE_NOT_CLOSED",f"outline has {len(bad)} non-degree-2 endpoints"))
    else:r.issues.append(ValidationIssue("warning","NO_BOARD_OUTLINE","no board outline was reconstructed"))
    if not board.nets and (board.pads or board.tracks):r.issues.append(ValidationIssue("error","NO_CONNECTIVITY","copper objects exist but no connectivity groups were generated"))
    return r
