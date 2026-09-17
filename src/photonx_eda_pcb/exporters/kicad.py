from __future__ import annotations
import shutil
import subprocess
import uuid
from pathlib import Path
from ..models import BoardModel


def _u(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "https://photonx.local/" + name))


def _q(text: str) -> str:
    return '"' + text.replace('\\', '\\\\').replace('"', '\\"') + '"'


def export_kicad(board: BoardModel, path: str | Path) -> Path:
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    net_num = {net.id: i + 1 for i, net in enumerate(board.nets)}
    lines = [
        '(kicad_pcb (version 20240108) (generator "photonx_eda_pcb")',
        '  (general (thickness 1.6))', '  (paper "A4")', '  (layers',
        '    (0 "F.Cu" signal)', '    (31 "B.Cu" signal)',
        '    (36 "B.SilkS" user "b.silkscreen")', '    (37 "F.SilkS" user "f.silkscreen")',
        '    (44 "Edge.Cuts" user)', '  )', '  (setup (pad_to_mask_clearance 0))', '  (net 0 "")',
    ]
    for net in board.nets: lines.append(f'  (net {net_num[net.id]} {_q(net.label or net.id)})')
    for pad in board.pads:
        n = net_num.get(pad.net_id, 0); net_name = next((net.label or net.id for net in board.nets if net.id == pad.net_id), "")
        shape = "circle" if pad.shape == "C" else "rect"; pad_type = "thru_hole" if pad.drill else "smd"
        layers = '"*.Cu" "*.Mask"' if pad.drill else f'"{pad.layer}" "F.Paste" "F.Mask"'
        lines += [f'  (footprint "PHOTONX:RecoveredPad" (layer {_q(pad.layer)}) (uuid {_u("fp:"+pad.id)})', f'    (at {pad.center.x:.6f} {pad.center.y:.6f})', f'    (property "Reference" {_q(pad.id)} (at 0 -2 0) (layer "F.SilkS") hide (uuid {_u("ref:"+pad.id)}))']
        drill = f' (drill {pad.drill:.6f})' if pad.drill else ""
        lines.append(f'    (pad "1" {pad_type} {shape} (at 0 0) (size {pad.size_x:.6f} {pad.size_y:.6f}){drill} (layers {layers}) (net {n} {_q(net_name)}) (uuid {_u("pad:"+pad.id)}))'); lines.append('  )')
    for trk in board.tracks:
        n = net_num.get(trk.net_id, 0); lines.append(f'  (segment (start {trk.start.x:.6f} {trk.start.y:.6f}) (end {trk.end.x:.6f} {trk.end.y:.6f}) (width {trk.width:.6f}) (layer {_q(trk.layer)}) (net {n}) (uuid {_u("track:"+trk.id)}))')
    for seg in board.outline:
        lines.append(f'  (gr_line (start {seg.start.x:.6f} {seg.start.y:.6f}) (end {seg.end.x:.6f} {seg.end.y:.6f}) (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid {_u("edge:"+seg.id)}))')
    lines.append(')'); p.write_text("\n".join(lines) + "\n", encoding="utf-8"); return p


def validate_with_kicad_cli(path: str | Path) -> tuple[bool | None, str]:
    exe = shutil.which("kicad-cli")
    if not exe: return None, "kicad-cli not found"
    proc = subprocess.run([exe, "pcb", "drc", str(path), "--exit-code-violations"], capture_output=True, text=True)
    return proc.returncode == 0, (proc.stdout + proc.stderr).strip()
