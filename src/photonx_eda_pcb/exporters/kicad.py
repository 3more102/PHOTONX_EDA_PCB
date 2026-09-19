from __future__ import annotations
import shutil,subprocess,uuid
from pathlib import Path
from math import isfinite
from ..models import BoardModel
from ..io.safe_write import atomic_write_text
from .kicad_report import KicadExportReport,KicadExportIssue
from .kicad_policy import pad_shape_name,slot_geometry,slot_export_status
from photonx_eda_pcb.plated_slot_inference import infer_plated_slot_padstack

def _u(name:str)->str:return str(uuid.uuid5(uuid.NAMESPACE_URL,"https://photonx.local/"+name))
def _q(text:str)->str:return '"'+text.replace("\\","\\\\").replace('"','\\"')+'"'

def _pad_lines(board,net_num,report):
    lines=[]
    for pad in board.pads:
        n=net_num.get(pad.net_id,0);net_name=next((net.label or net.id for net in board.nets if net.id==pad.net_id),"")
        shape=pad_shape_name(pad.shape);pad_type="thru_hole" if pad.drill else "smd"
        layers='"*.Cu" "*.Mask"' if pad.drill else f'"{pad.layer}" "F.Paste" "F.Mask"'
        angle=float(getattr(pad,"rotation_deg",getattr(pad,"rotation",0.0)) or 0.0)
        lines += [f'  (footprint "PHOTONX:RecoveredPad" (layer {_q(pad.layer)}) (uuid {_u("fp:"+pad.id)})',
                  f'    (at {pad.center.x:.6f} {pad.center.y:.6f})',
                  f'    (property "Reference" {_q(pad.id)} (at 0 -2 0) (layer "F.SilkS") hide (uuid {_u("ref:"+pad.id)}))']
        drill=f' (drill {pad.drill:.6f})' if pad.drill else ""
        lines.append(f'    (pad "1" {pad_type} {shape} (at 0 0 {angle:.6f}) (size {pad.size_x:.6f} {pad.size_y:.6f}){drill} (layers {layers}) (net {n} {_q(net_name)}) (uuid {_u("pad:"+pad.id)}))')
        lines.append('  )')
        if str(pad.shape).upper() not in {"C","R","O"}:report.issues.append(KicadExportIssue("warning","KICAD_PAD_SHAPE_FALLBACK",pad.id,f"unsupported reconstructed pad shape {pad.shape}; exported as rect"))
    return lines

def _record_skip(report,slot,code,msg):
    report.skipped_slots+=1;report.skipped_slot_ids.append(slot.id);report.issues.append(KicadExportIssue("warning",code,slot.id,msg))

def _npth_slot_lines(slot,report):
    g=slot_geometry(slot);cx,cy=g["center"];long_dim=g["long_mm"];short_dim=g["short_mm"];angle=g["angle_deg"]
    report.exported_slots+=1;report.exported_npth_slots+=1;report.exported_slot_ids.append(slot.id)
    return [
      f'  (footprint "PHOTONX:RecoveredNPTHSlot" (layer "F.Cu") (uuid {_u("slot-fp:"+slot.id)})',
      f'    (at {cx:.6f} {cy:.6f})',
      f'    (property "Reference" {_q(slot.id)} (at 0 -2 0) (layer "F.SilkS") hide (uuid {_u("slot-ref:"+slot.id)}))',
      f'    (pad "" np_thru_hole oval (at 0 0 {angle:.6f}) (size {long_dim:.6f} {short_dim:.6f}) (drill oval {long_dim:.6f} {short_dim:.6f}) (layers "*.Cu" "*.Mask") (uuid {_u("slot-pad:"+slot.id)}))',
      '  )'
    ]

def _plated_slot_lines(board,slot,net_num,report):
    inf=infer_plated_slot_padstack(board,slot)
    if inf.padstack is None:
        _record_skip(report,slot,"KICAD_SLOT_PLATED_UNSUPPORTED",";".join(inf.blockers));return []
    p=inf.padstack;shape=pad_shape_name(p.pad_shape);n=net_num.get(p.net_id,0)
    net_name=next((net.label or net.id for net in board.nets if net.id==p.net_id),"")
    layer_tokens=" ".join(_q(x) for x in p.layers)+' "*.Mask"'
    cx,cy=p.center;pw,ph=p.pad_size;dl,ds=p.drill_size
    report.exported_slots+=1;report.exported_plated_slots+=1;report.exported_slot_ids.append(slot.id)
    return [
      f'  (footprint "PHOTONX:RecoveredPlatedSlot" (layer "F.Cu") (uuid {_u("slot-fp:"+slot.id)})',
      f'    (at {cx:.6f} {cy:.6f})',
      f'    (property "Reference" {_q(slot.id)} (at 0 -2 0) (layer "F.SilkS") hide (uuid {_u("slot-ref:"+slot.id)}))',
      f'    (pad "1" thru_hole {shape} (at 0 0 {p.angle_deg:.6f}) (size {pw:.6f} {ph:.6f}) (drill oval {dl:.6f} {ds:.6f}) (layers {layer_tokens}) (net {n} {_q(net_name)}) (uuid {_u("slot-pad:"+slot.id)}))',
      '  )'
    ]

def _record_region_skips(board,report):
    for region in getattr(board,"regions",()):
        report.skipped_regions+=1
        report.skipped_region_ids.append(region.id)
        report.issues.append(KicadExportIssue(
            "warning",
            "KICAD_COPPER_REGION_UNSUPPORTED",
            region.id,
            "copper region export as a KiCad zone is not implemented; region omitted",
        ))

def _slot_lines(board,net_num,report):
    lines=[]
    for slot in getattr(board,"slots",()):
        status=slot_export_status(slot)
        if status=="export-npth":lines.extend(_npth_slot_lines(slot,report))
        elif status=="infer-plated-padstack":lines.extend(_plated_slot_lines(board,slot,net_num,report))
        else:_record_skip(report,slot,"KICAD_SLOT_PLATING_UNKNOWN","slot plating is unknown")
    return lines

def export_kicad_with_report(board:BoardModel,path:str|Path)->tuple[Path,KicadExportReport]:
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);report=KicadExportReport();net_num={net.id:i+1 for i,net in enumerate(board.nets)}
    lines=['(kicad_pcb (version 20240108) (generator "photonx_eda_pcb")','  (general (thickness 1.6))','  (paper "A4")','  (layers','    (0 "F.Cu" signal)','    (31 "B.Cu" signal)','    (36 "B.SilkS" user "b.silkscreen")','    (37 "F.SilkS" user "f.silkscreen")','    (44 "Edge.Cuts" user)','  )','  (setup (pad_to_mask_clearance 0))','  (net 0 "")']
    for net in board.nets:lines.append(f'  (net {net_num[net.id]} {_q(net.label or net.id)})')
    lines.extend(_pad_lines(board,net_num,report));lines.extend(_slot_lines(board,net_num,report));_record_region_skips(board,report)
    for trk in board.tracks:
        n=net_num.get(trk.net_id,0);lines.append(f'  (segment (start {trk.start.x:.6f} {trk.start.y:.6f}) (end {trk.end.x:.6f} {trk.end.y:.6f}) (width {trk.width:.6f}) (layer {_q(trk.layer)}) (net {n}) (uuid {_u("track:"+trk.id)}))')
    for seg in board.outline:lines.append(f'  (gr_line (start {seg.start.x:.6f} {seg.start.y:.6f}) (end {seg.end.x:.6f} {seg.end.y:.6f}) (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid {_u("edge:"+seg.id)}))')
    lines.append(')');atomic_write_text(p,"\n".join(lines)+"\n");return p,report
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
