from __future__ import annotations
import re,shutil,subprocess
from pathlib import Path
from math import isfinite
from ..models import BoardModel
from ..kicad_identity import photonx_uuid
from ..geometry_kernel.regions import region_shape
from .kicad_report import KicadExportReport,KicadExportIssue
from .kicad_policy import pad_export_descriptor,pad_shape_name,slot_geometry,slot_export_status,proven_via_span_omissions
from photonx_eda_pcb.excellon_routing import assess_route_export_readiness
from photonx_eda_pcb.plated_slot_inference import infer_plated_slot_padstack

def _q(text:str)->str:return '"'+text.replace("\\","\\\\").replace('"','\\"').replace("\n","\\n").replace("\r","\\r")+'"'


def _net_binding(board,net_num,net_id,object_id,report):
    if net_id is None:
        return 0,"",True
    n=net_num.get(net_id)
    if n is None:
        report.issues.append(KicadExportIssue(
            "warning",
            "KICAD_NET_REFERENCE_UNRESOLVED",
            object_id,
            f"object references unknown net {net_id!r}; exporter will not claim net 0 for this unresolved reference",
        ))
        return None,"",False
    net_name=next((net.label or net.id for net in board.nets if net.id==net_id),"")
    return n,net_name,True


_INNER_COPPER_LAYER_RE=re.compile(r"^In([1-9]|[12][0-9]|30)\.Cu$")

def _inner_copper_layers(board):
    observed={str(getattr(obj,"layer","")) for obj in [*board.tracks,*board.pads,*getattr(board,"regions",())]}
    indices=[]
    for name in observed:
        match=_INNER_COPPER_LAYER_RE.fullmatch(name)
        if match:indices.append(int(match.group(1)))
    highest=max(indices,default=0)
    return tuple((index,f"In{index}.Cu") for index in range(1,highest+1))

def _declared_copper_layer_names(board):
    return {"F.Cu","B.Cu"} | {name for _,name in _inner_copper_layers(board)}

def _copper_layer_lines(board):
    return [
        '    (0 "F.Cu" signal)',
        *(f'    ({ordinal} "{name}" signal)' for ordinal,name in _inner_copper_layers(board)),
        '    (31 "B.Cu" signal)',
    ]


def _pad_lines(board,net_num,report):
    lines=[]
    for pad in board.pads:
        n,net_name,net_known=_net_binding(board,net_num,pad.net_id,pad.id,report)
        descriptor,ref_layer,layer_warning=pad_export_descriptor(pad)
        shape=descriptor["shape"];pad_type=descriptor["kind"]
        layers=" ".join(_q(x) for x in descriptor["layers"])
        angle=descriptor["pad_angle"]
        lines += [f'  (footprint "PHOTONX:RecoveredPad" (layer {_q(descriptor["footprint_layer"])}) (uuid {photonx_uuid("fp:"+pad.id)})',
                  f'    (at {pad.center.x:.6f} {pad.center.y:.6f})',
                  f'    (property "Reference" {_q(pad.id)} (at 0 -2 0) (layer {_q(ref_layer)}) hide (uuid {photonx_uuid("ref:"+pad.id)}))']
        drill=f' (drill {pad.drill:.6f})' if pad.drill else ""
        net_clause=f' (net {n} {_q(net_name)})' if net_known else ""
        lines.append(f'    (pad "1" {pad_type} {shape} (at 0 0 {angle:.6f}) (size {pad.size_x:.6f} {pad.size_y:.6f}){drill} (layers {layers}){net_clause} (uuid {photonx_uuid("pad:"+pad.id)}))')
        lines.append('  )')
        if str(pad.shape).upper() not in {"C","R","O"}:report.issues.append(KicadExportIssue("warning","KICAD_PAD_SHAPE_FALLBACK",pad.id,f"unsupported reconstructed pad shape {pad.shape}; exported as rect"))
        if layer_warning:report.issues.append(KicadExportIssue("warning","KICAD_SMD_NON_SURFACE_LAYER",pad.id,layer_warning))
    return lines

def _record_skip(report,slot,code,msg):
    report.skipped_slots+=1;report.skipped_slot_ids.append(slot.id);report.issues.append(KicadExportIssue("warning",code,slot.id,msg))

def _npth_slot_lines(slot,report):
    g=slot_geometry(slot);cx,cy=g["center"];long_dim=g["long_mm"];short_dim=g["short_mm"];angle=g["angle_deg"]
    report.exported_slots+=1;report.exported_npth_slots+=1;report.exported_slot_ids.append(slot.id)
    return [
      f'  (footprint "PHOTONX:RecoveredNPTHSlot" (layer "F.Cu") (uuid {photonx_uuid("slot-fp:"+slot.id)})',
      f'    (at {cx:.6f} {cy:.6f})',
      f'    (property "Reference" {_q(slot.id)} (at 0 -2 0) (layer "F.SilkS") hide (uuid {photonx_uuid("slot-ref:"+slot.id)}))',
      f'    (pad "" np_thru_hole oval (at 0 0 {angle:.6f}) (size {long_dim:.6f} {short_dim:.6f}) (drill oval {long_dim:.6f} {short_dim:.6f}) (layers "*.Cu" "*.Mask") (uuid {photonx_uuid("slot-pad:"+slot.id)}))',
      '  )'
    ]

def _plated_slot_lines(board,slot,net_num,report):
    inf=infer_plated_slot_padstack(board,slot)
    if inf.padstack is None:
        _record_skip(report,slot,"KICAD_SLOT_PLATED_UNSUPPORTED",";".join(inf.blockers));return []
    p=inf.padstack;shape=pad_shape_name(p.pad_shape)
    n,net_name,net_known=_net_binding(board,net_num,p.net_id,slot.id,report)
    layer_tokens=" ".join(_q(x) for x in p.layers)+' "*.Mask"'
    cx,cy=p.center;pw,ph=p.pad_size;dl,ds=p.drill_size
    net_clause=f' (net {n} {_q(net_name)})' if net_known else ""
    report.exported_slots+=1;report.exported_plated_slots+=1;report.exported_slot_ids.append(slot.id)
    return [
      f'  (footprint "PHOTONX:RecoveredPlatedSlot" (layer "F.Cu") (uuid {photonx_uuid("slot-fp:"+slot.id)})',
      f'    (at {cx:.6f} {cy:.6f})',
      f'    (property "Reference" {_q(slot.id)} (at 0 -2 0) (layer "F.SilkS") hide (uuid {photonx_uuid("slot-ref:"+slot.id)}))',
      f'    (pad "1" thru_hole {shape} (at 0 0 {p.angle_deg:.6f}) (size {pw:.6f} {ph:.6f}) (drill oval {dl:.6f} {ds:.6f}) (layers {layer_tokens}){net_clause} (uuid {photonx_uuid("slot-pad:"+slot.id)}))',
      '  )'
    ]

def _record_region_skip(report,region,code,msg):
    report.skipped_regions+=1
    report.skipped_region_ids.append(region.id)
    report.issues.append(KicadExportIssue("warning",code,region.id,msg))

def _ring_coords(points):
    points=list(points)
    if len(points)>1 and points[0].x==points[-1].x and points[0].y==points[-1].y:
        points=points[:-1]
    coords=[(float(point.x),float(point.y)) for point in points]
    if len(set(coords))<3 or any(not isfinite(value) for pair in coords for value in pair):
        return None
    return coords

def _region_points(region):
    return _ring_coords(region.points)

def _region_lines(board,net_num,report):
    lines=[]
    declared_copper_layers=_declared_copper_layer_names(board)
    for region in getattr(board,"regions",()):
        if region.layer not in declared_copper_layers:
            _record_region_skip(
                report,
                region,
                "KICAD_COPPER_REGION_LAYER_UNSUPPORTED",
                f"copper region layer {region.layer!r} is not a declared canonical KiCad copper layer",
            )
            continue

        holes=tuple(getattr(region,"holes",()))
        rings=[region.points,*holes]
        ring_coords=[_ring_coords(ring) for ring in rings]
        if any(coords is None for coords in ring_coords):
            _record_region_skip(
                report,
                region,
                "KICAD_COPPER_REGION_INVALID_GEOMETRY",
                "copper region shell and hole rings must each contain at least three distinct finite vertices",
            )
            continue

        try:
            shape=region_shape(region)
        except (TypeError,ValueError,OverflowError):
            shape=None
        if shape is None or shape.is_empty or not shape.is_valid or not isfinite(float(shape.area)) or shape.area<=0:
            _record_region_skip(
                report,
                region,
                "KICAD_COPPER_REGION_INVALID_GEOMETRY",
                "copper region shell/holes do not form one valid positive-area polygon",
            )
            continue

        if region.net_id is None:
            n=0;net_name=""
        elif region.net_id not in net_num:
            _record_region_skip(
                report,
                region,
                "KICAD_COPPER_REGION_NET_UNRESOLVED",
                f"copper region references unknown net {region.net_id!r}",
            )
            continue
        else:
            n=net_num[region.net_id]
            net_name=next((net.label or net.id for net in board.nets if net.id==region.net_id),"")

        zone_lines=[
            "  (zone",
            f"    (net {n})",
            f"    (net_name {_q(net_name)})",
            f"    (layer {_q(region.layer)})",
            f'    (uuid {photonx_uuid("region:"+region.id)})',
            f'    (name {_q("PHOTONX:"+region.id)})',
            "    (hatch edge 0.500000)",
            "    (connect_pads (clearance 0.500000))",
            "    (min_thickness 0.250000)",
        ]
        if holes:
            zone_lines.append("    (fill)")
        else:
            zone_lines.append("    (fill yes (thermal_gap 0.500000) (thermal_bridge_width 0.500000) (island_removal_mode 1))")

        for ring in ring_coords:
            pts=" ".join(f"(xy {x:.6f} {y:.6f})" for x,y in ring)
            zone_lines.append(f"    (polygon (pts {pts}))")

        if not holes:
            pts=" ".join(f"(xy {x:.6f} {y:.6f})" for x,y in ring_coords[0])
            zone_lines.append(f"    (filled_polygon (layer {_q(region.layer)}) (pts {pts}))")
        zone_lines.append("  )")
        lines.extend(zone_lines)

        report.exported_regions+=1
        report.exported_region_ids.append(region.id)
        if holes:
            report.issues.append(KicadExportIssue(
                "warning",
                "KICAD_COPPER_REGION_FILL_CACHE_OMITTED",
                region.id,
                "zone shell and holes were exported exactly; cached fill was omitted so KiCad must repour using exporter-default zone rules",
            ))
        report.issues.append(KicadExportIssue(
            "warning",
            "KICAD_COPPER_REGION_ZONE_RULES_DEFAULTED",
            region.id,
            "KiCad repour clearance and thermal rules use exporter defaults because Gerber does not preserve the original zone-design rules",
        ))
    return lines

def _record_via_span_skips(board,report):
    omitted,problems=proven_via_span_omissions(board)
    for object_id,message in problems:
        report.issues.append(KicadExportIssue(
            "error",
            "KICAD_VIA_SPAN_METADATA_INVALID",
            object_id,
            message,
        ))
    for drill_id in omitted:
        report.skipped_via_spans+=1
        report.skipped_via_span_ids.append(drill_id)
        report.issues.append(KicadExportIssue(
            "warning",
            "KICAD_PROVEN_VIA_SPAN_UNSUPPORTED",
            drill_id,
            "proven plated via span is part of source connectivity, but the current KiCad exporter does not synthesize drill-derived annular via geometry; vertical bridge omitted",
        ))

def _record_route_skips(board,report):
    readiness=assess_route_export_readiness(getattr(board,"routes",()))
    for route_id in readiness.omitted:
        report.skipped_routes+=1
        report.skipped_route_ids.append(route_id)
        report.issues.append(KicadExportIssue(
            "warning",
            readiness.reasons[route_id],
            route_id,
            "arbitrary routed milling is preserved in PHOTONX but cannot be represented faithfully by the current KiCad exporter; route omitted",
        ))


def _slot_lines(board,net_num,report):
    lines=[]
    for slot in getattr(board,"slots",()):
        status=slot_export_status(slot)
        if status=="export-npth":lines.extend(_npth_slot_lines(slot,report))
        elif status=="infer-plated-padstack":lines.extend(_plated_slot_lines(board,slot,net_num,report))
        else:_record_skip(report,slot,"KICAD_SLOT_PLATING_UNKNOWN","slot plating is unknown")
    return lines

def _track_lines(board,net_num,report):
    lines=[]
    declared_copper_layers=_declared_copper_layer_names(board)
    for trk in board.tracks:
        layer_known=trk.layer in declared_copper_layers
        if not layer_known:
            report.issues.append(KicadExportIssue(
                "warning",
                "KICAD_TRACK_LAYER_UNSUPPORTED",
                trk.id,
                f"track layer {trk.layer!r} is not a declared canonical KiCad copper layer",
            ))
        n,_,net_known=_net_binding(board,net_num,trk.net_id,trk.id,report)
        if not (layer_known and net_known):
            report.skipped_tracks+=1
            report.skipped_track_ids.append(trk.id)
            continue
        lines.append(f'  (segment (start {trk.start.x:.6f} {trk.start.y:.6f}) (end {trk.end.x:.6f} {trk.end.y:.6f}) (width {trk.width:.6f}) (layer {_q(trk.layer)}) (net {n}) (uuid {photonx_uuid("track:"+trk.id)}))')
        report.exported_tracks+=1
        report.exported_track_ids.append(trk.id)
    return lines

def export_kicad_with_report(board:BoardModel,path:str|Path)->tuple[Path,KicadExportReport]:
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);report=KicadExportReport();net_num={net.id:i+1 for i,net in enumerate(board.nets)}
    lines=['(kicad_pcb (version 20240108) (generator "photonx_eda_pcb")','  (general (thickness 1.6))','  (paper "A4")','  (layers',*_copper_layer_lines(board),'    (36 "B.SilkS" user "b.silkscreen")','    (37 "F.SilkS" user "f.silkscreen")','    (44 "Edge.Cuts" user)','  )','  (setup (pad_to_mask_clearance 0))','  (net 0 "")']
    for net in board.nets:lines.append(f'  (net {net_num[net.id]} {_q(net.label or net.id)})')
    lines.extend(_pad_lines(board,net_num,report));lines.extend(_slot_lines(board,net_num,report));lines.extend(_region_lines(board,net_num,report));lines.extend(_track_lines(board,net_num,report));_record_via_span_skips(board,report);_record_route_skips(board,report)
    for seg in board.outline:lines.append(f'  (gr_line (start {seg.start.x:.6f} {seg.start.y:.6f}) (end {seg.end.x:.6f} {seg.end.y:.6f}) (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid {photonx_uuid("edge:"+seg.id)}))')
    lines.append(')');p.write_text("\n".join(lines)+"\n",encoding="utf-8");return p,report
def export_kicad(board:BoardModel,path:str|Path)->Path:return export_kicad_with_report(board,path)[0]
def validate_with_kicad_cli(path:str|Path,*,timeout_s:float=30.0)->tuple[bool|None,str]:
    try:timeout=float(timeout_s)
    except (TypeError,ValueError) as exc:raise ValueError("timeout_s must be a positive finite number") from exc
    if not isfinite(timeout) or timeout<=0:raise ValueError("timeout_s must be a positive finite number")
    exe=shutil.which("kicad-cli")
    if not exe:return None,"kicad-cli not found"
    try:
        proc=subprocess.run([exe,"pcb","drc",str(path),"--exit-code-violations"],capture_output=True,text=True,timeout=timeout)
    except subprocess.TimeoutExpired:return None,f"kicad-cli validation timed out after {timeout:g}s"
    except OSError as exc:return None,f"kicad-cli failed to start: {exc}"
    return proc.returncode==0,(proc.stdout+proc.stderr).strip()
