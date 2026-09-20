from __future__ import annotations
import shutil,subprocess
from pathlib import Path
from math import isfinite
from ..models import BoardModel
from ..kicad_identity import photonx_uuid
from ..geometry_kernel.regions import region_shape
from .kicad_report import KicadExportReport,KicadExportIssue
from .kicad_policy import KICAD_BOARD_FORMAT_VERSION,KICAD_GENERATOR,KICAD_DEFAULT_BOARD_THICKNESS_MM,KICAD_DEFAULT_PAD_TO_MASK_CLEARANCE_MM,KICAD_DEFAULT_PAPER,declared_copper_layer_names,drill_export_status,kicad_board_layer_specs,kicad_duplicate_object_ids,kicad_net_export_rows,outline_export_status,pad_export_descriptor,pad_export_status,pad_shape_name,slot_geometry,slot_export_status,track_export_status,proven_via_span_omissions
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


def _board_layer_lines(board):
    lines=[]
    for row in kicad_board_layer_specs(board):
        suffix=f' {_q(row["suffix"])}' if row["suffix"] else ""
        lines.append(
            f'    ({row["id"]} {_q(row["name"])} {row["type"]}{suffix})'
        )
    return lines


def _outline_lines(board, report, duplicate_object_ids=()):
    lines = []
    duplicate_object_ids=set(duplicate_object_ids)
    for segment in board.outline:
        if segment.id in duplicate_object_ids:
            report.skipped_outline += 1
            if segment.id not in report.skipped_outline_ids:
                report.skipped_outline_ids.append(segment.id)
            continue
        status = outline_export_status(segment)
        if status != "export":
            report.skipped_outline += 1
            report.skipped_outline_ids.append(segment.id)
            if status == "skip-zero-length":
                code = "KICAD_OUTLINE_ZERO_LENGTH"
                message = (
                    "outline segment start and end are identical; segment omitted"
                )
            else:
                code = "KICAD_OUTLINE_COORDINATE_INVALID"
                message = (
                    "outline segment coordinates must be finite numeric values; "
                    "segment omitted"
                )
            report.issues.append(
                KicadExportIssue(
                    "warning",
                    code,
                    segment.id,
                    message,
                )
            )
            continue

        sx = float(segment.start.x)
        sy = float(segment.start.y)
        ex = float(segment.end.x)
        ey = float(segment.end.y)
        lines.append(
            (
                f'  (gr_line (start {sx:.6f} {sy:.6f}) '
                f'(end {ex:.6f} {ey:.6f}) '
                f'(stroke (width 0.1) (type default)) '
                f'(layer "Edge.Cuts") '
                f'(uuid {photonx_uuid("edge:"+segment.id)}))'
            )
        )
        report.exported_outline += 1
        report.exported_outline_ids.append(segment.id)
    return lines


def _record_drill_skip(report, drill, code, message):
    report.skipped_drills += 1
    report.skipped_drill_ids.append(drill.id)
    report.issues.append(
        KicadExportIssue(
            "warning",
            code,
            drill.id,
            message,
        )
    )


def _drill_lines(board, report, duplicate_object_ids=()):
    lines = []
    duplicate_object_ids=set(duplicate_object_ids)
    for drill in board.drills:
        if drill.id in duplicate_object_ids:
            report.skipped_drills += 1
            if drill.id not in report.skipped_drill_ids:
                report.skipped_drill_ids.append(drill.id)
            continue
        status = drill_export_status(drill)
        if status != "export-npth":
            if status == "skip-unknown-plating":
                code = "KICAD_DRILL_PLATING_UNKNOWN"
                message = (
                    "point-drill plating is unknown; drill omitted instead of "
                    "being guessed as NPTH or plated"
                )
            elif status == "skip-plated-padstack":
                code = "KICAD_DRILL_PLATED_PADSTACK_UNSUPPORTED"
                message = (
                    "plated point drill has no standalone annular pad-stack "
                    "contract; drill omitted instead of being mislabeled NPTH"
                )
            elif status == "skip-invalid-geometry":
                code = "KICAD_DRILL_GEOMETRY_INVALID"
                message = "point-drill diameter must be finite and positive"
            else:
                code = "KICAD_DRILL_PLATING_UNSUPPORTED"
                message = (
                    f"unsupported point-drill plating value {drill.plating!r}"
                )
            _record_drill_skip(report, drill, code, message)
            continue

        diameter = float(drill.diameter)
        report.exported_drills += 1
        report.exported_drill_ids.append(drill.id)
        lines.extend(
            [
                (
                    f'  (footprint "PHOTONX:RecoveredNPTHDrill" '
                    f'(layer "F.Cu") '
                    f'(uuid {photonx_uuid("drill-fp:"+drill.id)})'
                ),
                f'    (at {drill.center.x:.6f} {drill.center.y:.6f})',
                (
                    f'    (property "Reference" {_q(drill.id)} '
                    f'(at 0 -2 0) (layer "F.SilkS") hide '
                    f'(uuid {photonx_uuid("drill-ref:"+drill.id)}))'
                ),
                (
                    f'    (pad "" np_thru_hole circle (at 0 0 0) '
                    f'(size {diameter:.6f} {diameter:.6f}) '
                    f'(drill {diameter:.6f}) '
                    f'(layers "*.Cu" "*.Mask") '
                    f'(uuid {photonx_uuid("drill-pad:"+drill.id)}))'
                ),
                "  )",
            ]
        )
    return lines


def _pad_lines(board,net_num,report,duplicate_object_ids=()):
    lines=[]
    duplicate_object_ids=set(duplicate_object_ids)
    for pad in board.pads:
        if pad.id in duplicate_object_ids:
            report.skipped_pads+=1
            if pad.id not in report.skipped_pad_ids:
                report.skipped_pad_ids.append(pad.id)
            continue
        status=pad_export_status(board,pad)
        if status!="export":
            report.skipped_pads+=1
            report.skipped_pad_ids.append(pad.id)
            if status=="skip-invalid-coordinate":
                report.issues.append(KicadExportIssue(
                    "warning",
                    "KICAD_PAD_COORDINATE_INVALID",
                    pad.id,
                    "recovered pad center coordinates must be finite numeric values; pad omitted",
                ))
            elif status=="skip-invalid-size":
                report.issues.append(KicadExportIssue(
                    "warning",
                    "KICAD_PAD_SIZE_INVALID",
                    pad.id,
                    "recovered pad dimensions must be finite positive numbers; pad omitted",
                ))
            elif status=="skip-invalid-rotation":
                report.issues.append(KicadExportIssue(
                    "warning",
                    "KICAD_PAD_ROTATION_INVALID",
                    pad.id,
                    "recovered pad rotation must be a finite numeric value; pad omitted",
                ))
            elif status=="skip-layer":
                report.issues.append(KicadExportIssue(
                    "warning",
                    "KICAD_PAD_LAYER_UNSUPPORTED",
                    pad.id,
                    f"recovered pad layer {pad.layer!r} is not a declared canonical KiCad copper layer; pad omitted",
                ))
            elif status=="skip-shape":
                report.issues.append(KicadExportIssue(
                    "warning",
                    "KICAD_PAD_SHAPE_UNSUPPORTED",
                    pad.id,
                    f"recovered pad shape {pad.shape!r} has no exact current KiCad pad mapping; pad omitted instead of approximated",
                ))
            else:
                report.issues.append(KicadExportIssue(
                    "warning",
                    "KICAD_PAD_DRILL_PADSTACK_UNPROVEN",
                    pad.id,
                    "drill overlap does not prove plated through-hole pad-stack semantics; recovered drilled pad omitted instead of inventing *.Cu copper",
                ))
            continue
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
        report.exported_pads+=1
        report.exported_pad_ids.append(pad.id)
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

def _region_lines(board,net_num,report,duplicate_object_ids=()):
    lines=[]
    declared_copper_layers=declared_copper_layer_names(board)
    duplicate_object_ids=set(duplicate_object_ids)
    for region in getattr(board,"regions",()):
        if region.id in duplicate_object_ids:
            report.skipped_regions+=1
            if region.id not in report.skipped_region_ids:
                report.skipped_region_ids.append(region.id)
            continue
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


def _slot_lines(board,net_num,report,duplicate_object_ids=()):
    lines=[]
    duplicate_object_ids=set(duplicate_object_ids)
    for slot in getattr(board,"slots",()):
        if slot.id in duplicate_object_ids:
            report.skipped_slots+=1
            if slot.id not in report.skipped_slot_ids:
                report.skipped_slot_ids.append(slot.id)
            continue
        status=slot_export_status(slot)
        if status=="export-npth":lines.extend(_npth_slot_lines(slot,report))
        elif status=="infer-plated-padstack":lines.extend(_plated_slot_lines(board,slot,net_num,report))
        else:_record_skip(report,slot,"KICAD_SLOT_PLATING_UNKNOWN","slot plating is unknown")
    return lines

def _track_lines(board,net_num,report,duplicate_object_ids=()):
    lines=[]
    duplicate_object_ids=set(duplicate_object_ids)
    for trk in board.tracks:
        if trk.id in duplicate_object_ids:
            report.skipped_tracks+=1
            if trk.id not in report.skipped_track_ids:
                report.skipped_track_ids.append(trk.id)
            continue
        status=track_export_status(board,trk)
        if status!="export":
            if status=="skip-layer":
                code="KICAD_TRACK_LAYER_UNSUPPORTED"
                message=(
                    f"track layer {trk.layer!r} is not a declared canonical "
                    "KiCad copper layer"
                )
            elif status=="skip-invalid-width":
                code="KICAD_TRACK_WIDTH_INVALID"
                message="track width must be a finite positive number"
            elif status=="skip-zero-length":
                code="KICAD_TRACK_ZERO_LENGTH"
                message="track start and end are identical"
            else:
                code="KICAD_TRACK_COORDINATE_INVALID"
                message="track coordinates must be finite numeric values"
            report.issues.append(
                KicadExportIssue("warning",code,trk.id,message)
            )
        n,_,net_known=_net_binding(board,net_num,trk.net_id,trk.id,report)
        if status!="export" or not net_known:
            report.skipped_tracks+=1
            report.skipped_track_ids.append(trk.id)
            continue

        sx=float(trk.start.x);sy=float(trk.start.y)
        ex=float(trk.end.x);ey=float(trk.end.y);width=float(trk.width)
        lines.append(
            f'  (segment (start {sx:.6f} {sy:.6f}) '
            f'(end {ex:.6f} {ey:.6f}) (width {width:.6f}) '
            f'(layer {_q(str(trk.layer))}) (net {n}) '
            f'(uuid {photonx_uuid("track:"+trk.id)}))'
        )
        report.exported_tracks+=1
        report.exported_track_ids.append(trk.id)
    return lines

def export_kicad_with_report(board:BoardModel,path:str|Path)->tuple[Path,KicadExportReport]:
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);report=KicadExportReport()
    net_rows,duplicate_net_ids=kicad_net_export_rows(board)
    duplicate_object_ids=kicad_duplicate_object_ids(board)
    net_num={row["id"]:row["code"] for row in net_rows}
    for object_id in duplicate_object_ids:
        report.issues.append(KicadExportIssue(
            "error",
            "KICAD_OBJECT_ID_DUPLICATE",
            str(object_id),
            "duplicate source physical-object ID is ambiguous; every exportable object with this ID is omitted before deterministic KiCad UUID generation",
        ))
    for net_id in duplicate_net_ids:
        report.issues.append(KicadExportIssue(
            "error",
            "KICAD_NET_ID_DUPLICATE",
            str(net_id),
            "duplicate source net ID is ambiguous; all definitions with this ID are omitted from the KiCad net table instead of choosing one ordinal",
        ))
    lines=[
        f'(kicad_pcb (version {KICAD_BOARD_FORMAT_VERSION}) (generator {_q(KICAD_GENERATOR)})',
        f'  (general (thickness {KICAD_DEFAULT_BOARD_THICKNESS_MM:g}))',
        f'  (paper {_q(KICAD_DEFAULT_PAPER)})',
        '  (layers',
        *_board_layer_lines(board),
        '  )',
        f'  (setup (pad_to_mask_clearance {KICAD_DEFAULT_PAD_TO_MASK_CLEARANCE_MM:g}))',
        '  (net 0 "")',
    ]
    for row in net_rows:lines.append(f'  (net {row["code"]} {_q(row["name"])})')
    lines.extend(_drill_lines(board,report,duplicate_object_ids));lines.extend(_pad_lines(board,net_num,report,duplicate_object_ids));lines.extend(_slot_lines(board,net_num,report,duplicate_object_ids));lines.extend(_region_lines(board,net_num,report,duplicate_object_ids));lines.extend(_track_lines(board,net_num,report,duplicate_object_ids));_record_via_span_skips(board,report);_record_route_skips(board,report)
    lines.extend(_outline_lines(board,report,duplicate_object_ids))
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
