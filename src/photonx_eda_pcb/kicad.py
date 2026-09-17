from __future__ import annotations
from pathlib import Path
from .models import BoardModel


def export_kicad(board: BoardModel, path: str | Path):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    net_names=sorted(board.nets)
    net_id={n:i+1 for i,n in enumerate(net_names)}
    lines=['(kicad_pcb (version 20240108) (generator photonx_eda_pcb)','  (general (thickness 1.6))','  (paper "A4")','  (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "b.silkscreen") (37 "F.SilkS" user "f.silkscreen") (44 "Edge.Cuts" user))']
    for n in net_names: lines.append(f'  (net {net_id[n]} "{n}")')
    for s in board.outline.segments:
        lines.append(f'  (gr_line (start {s.start.x:.4f} {s.start.y:.4f}) (end {s.end.x:.4f} {s.end.y:.4f}) (stroke (width 0.1) (type default)) (layer "Edge.Cuts"))')
    for p in board.pads:
        n=net_id.get(p.net,0); drill=f' (drill {p.drill:.4f})' if p.drill else ''
        layers='"*.Cu" "*.Mask"' if p.drill else '"F.Cu" "F.Paste" "F.Mask"'
        typ='thru_hole' if p.drill else 'smd'
        shape='circle'
        lines += [f'  (footprint "PHOTONX:RecoveredPad" (layer "F.Cu") (at {p.center.x:.4f} {p.center.y:.4f})',f'    (property "Reference" "{p.id}" (at 0 -2 0) (layer "F.SilkS"))',f'    (pad "1" {typ} {shape} (at 0 0) (size {p.diameter:.4f} {p.diameter:.4f}){drill} (layers {layers}) (net {n} "{p.net or ""}"))', '  )']
    for t in board.tracks:
        n=net_id.get(t.net,0)
        lines.append(f'  (segment (start {t.start.x:.4f} {t.start.y:.4f}) (end {t.end.x:.4f} {t.end.y:.4f}) (width {t.width:.4f}) (layer "F.Cu") (net {n}))')
    lines.append(')')
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return path
