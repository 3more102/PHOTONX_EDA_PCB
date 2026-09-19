from __future__ import annotations
from collections import Counter
from dataclasses import dataclass,field
from math import isfinite
from .models import BoardModel
from .excellon_routing.validation import validate_route
from .geometry_kernel import region_shape
from .core.numeric import is_finite_number

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
    if isinstance(outline_tolerance_mm,bool):
        raise ValueError("outline_tolerance_mm must be a positive finite number")
    try: outline_tolerance=float(outline_tolerance_mm)
    except (TypeError,ValueError) as exc: raise ValueError("outline_tolerance_mm must be a positive finite number") from exc
    if not isfinite(outline_tolerance) or outline_tolerance<=0:
        raise ValueError("outline_tolerance_mm must be a positive finite number")
    r=ValidationReport()
    all_objects=[*board.tracks,*board.pads,*board.drills,*board.outline,*getattr(board,"slots",()),*getattr(board,"routes",()),*getattr(board,"regions",())]
    ids=[o.id for o in all_objects]
    if len(ids)!=len(set(ids)):r.issues.append(ValidationIssue("error","DUPLICATE_OBJECT_ID","object IDs must be globally unique"))
    idx=board.object_index();net_members=set()
    for net in board.nets:
        if not 0<=net.confidence<=1:r.issues.append(ValidationIssue("error","INVALID_NET_CONFIDENCE",f"invalid confidence for {net.id}",(net.id,)))
        for member in net.members:
            if member not in idx:r.issues.append(ValidationIssue("error","NET_MEMBER_MISSING",f"{net.id} references missing object {member}",(net.id,member)))
            if member in net_members:r.issues.append(ValidationIssue("error","OBJECT_IN_MULTIPLE_NETS",f"{member} appears in more than one physical net",(member,)))
            net_members.add(member)
    for obj in [*board.tracks,*board.pads,*getattr(board,"regions",())]:
        if obj.net_id and obj.id not in net_members:r.issues.append(ValidationIssue("error","OBJECT_NET_BACKREF_MISMATCH",f"{obj.id} has net_id but is not listed in that net",(obj.id,)))
    pad_ids={p.id for p in board.pads}
    component_id_counts=Counter(comp.id for comp in board.components)
    for component_id,count in sorted(component_id_counts.items()):
        if count>1:r.issues.append(ValidationIssue("error","DUPLICATE_COMPONENT_ID",f"duplicate component hypothesis id {component_id}",(component_id,)))
    for comp in board.components:
        duplicate_pad_ids=sorted(pid for pid,count in Counter(comp.pad_ids).items() if count>1)
        if duplicate_pad_ids:r.issues.append(ValidationIssue("error","COMPONENT_PAD_DUPLICATE",f"{comp.id} repeats pad ids {duplicate_pad_ids}",(comp.id,*duplicate_pad_ids)))
        missing=[pid for pid in comp.pad_ids if pid not in pad_ids]
        if missing:r.issues.append(ValidationIssue("error","COMPONENT_PAD_MISSING",f"{comp.id} references missing pads {missing}",(comp.id,*missing)))
        if not 0<=comp.confidence<=1:r.issues.append(ValidationIssue("error","INVALID_COMPONENT_CONFIDENCE",f"invalid confidence for {comp.id}",(comp.id,)))
    for slot in getattr(board,"slots",()):
        if not is_finite_number(slot.width_mm) or slot.width_mm<=0:
            r.issues.append(ValidationIssue("error","SLOT_WIDTH_INVALID","slot width must be a positive finite number",(slot.id,)))
        try:slot_coords=(*slot.start,*slot.end)
        except TypeError:slot_coords=()
        if len(slot_coords)!=4 or not all(is_finite_number(value) for value in slot_coords):
            r.issues.append(ValidationIssue("error","SLOT_COORDINATE_INVALID","slot coordinates must be finite numbers",(slot.id,)))
        elif slot_coords[:2]==slot_coords[2:]:
            r.issues.append(ValidationIssue("warning","SLOT_ZERO_LENGTH","slot start and end are identical",(slot.id,)))
        if slot.plated not in {"unknown","plated","non-plated","non_plated"}:r.issues.append(ValidationIssue("warning","SLOT_PLATING_UNKNOWN_ENUM",f"unexpected slot plating value {slot.plated}",(slot.id,)))
    for route in getattr(board,"routes",()):
        for code in validate_route(route):
            sev="warning" if code=="ROUTE_ZERO_LENGTH_SEGMENT" else "error"
            r.issues.append(ValidationIssue(sev,code,code.replace("_"," ").lower(),(route.id,)))
    for region in getattr(board,"regions",()):
        points=tuple(region.points)
        if len(points)<4 or points[0]!=points[-1]:
            r.issues.append(ValidationIssue("error","REGION_NOT_CLOSED","copper region must have a closed outer contour",(region.id,)))
            continue
        unique={(float(p.x),float(p.y)) for p in points[:-1]}
        if len(unique)<3:
            r.issues.append(ValidationIssue("error","REGION_VERTEX_COUNT_INVALID","copper region needs at least three unique outer vertices",(region.id,)))
            continue
        invalid_hole=False
        for hole_index,hole in enumerate(getattr(region,"holes",())):
            ring=tuple(hole)
            if len(ring)<4 or ring[0]!=ring[-1]:
                r.issues.append(ValidationIssue("error","REGION_HOLE_NOT_CLOSED",f"copper region hole {hole_index + 1} must be closed",(region.id,)))
                invalid_hole=True
                break
            hole_unique={(float(p.x),float(p.y)) for p in ring[:-1]}
            if len(hole_unique)<3:
                r.issues.append(ValidationIssue("error","REGION_HOLE_VERTEX_COUNT_INVALID",f"copper region hole {hole_index + 1} needs at least three unique vertices",(region.id,)))
                invalid_hole=True
                break
        if invalid_hole:
            continue
        shape=region_shape(region)
        if shape.is_empty or float(shape.area)<=0 or not shape.is_valid:
            r.issues.append(ValidationIssue("error","REGION_GEOMETRY_INVALID","copper region polygon with holes is empty, zero-area, or invalid",(region.id,)))
    if board.outline:
        degree={};invalid_outline=False
        def key_xy(x,y):return (round(x/outline_tolerance)*outline_tolerance,round(y/outline_tolerance)*outline_tolerance)
        for seg in board.outline:
            try:coords=tuple(float(v) for v in (seg.start.x,seg.start.y,seg.end.x,seg.end.y))
            except (TypeError,ValueError):coords=()
            if len(coords)!=4 or not all(isfinite(v) for v in coords):
                r.issues.append(ValidationIssue("error","OUTLINE_COORDINATE_INVALID","outline coordinates must be finite numbers",(seg.id,)))
                invalid_outline=True
                continue
            sx,sy,ex,ey=coords
            if sx==ex and sy==ey:
                r.issues.append(ValidationIssue("error","OUTLINE_SEGMENT_ZERO_LENGTH","outline segment start and end are identical",(seg.id,)))
                invalid_outline=True
                continue
            start_key=key_xy(sx,sy);end_key=key_xy(ex,ey)
            degree[start_key]=degree.get(start_key,0)+1;degree[end_key]=degree.get(end_key,0)+1
        if not invalid_outline:
            bad=[p for p,d in degree.items() if d!=2]
            if bad:r.issues.append(ValidationIssue("warning","OUTLINE_NOT_CLOSED",f"outline has {len(bad)} non-degree-2 endpoints"))
    else:r.issues.append(ValidationIssue("warning","NO_BOARD_OUTLINE","no board outline was reconstructed"))
    if not board.nets and (board.pads or board.tracks or getattr(board,"regions",())):r.issues.append(ValidationIssue("error","NO_CONNECTIVITY","copper objects exist but no connectivity groups were generated"))
    return r
