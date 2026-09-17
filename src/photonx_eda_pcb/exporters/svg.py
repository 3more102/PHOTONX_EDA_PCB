from pathlib import Path
from ..geometry.bbox import board_bounds
def export_svg(board,path:str|Path,padding:float=2.0)->Path:
    b=board_bounds(board); path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    if b is None: path.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>\n',encoding="utf-8"); return path
    w=b.width+2*padding; h=b.height+2*padding; ox=b.min_x-padding; oy=b.min_y-padding
    lines=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{ox} {oy} {w} {h}">']
    for t in board.tracks: lines.append(f'<line x1="{t.start.x}" y1="{t.start.y}" x2="{t.end.x}" y2="{t.end.y}" stroke="black" stroke-width="{t.width}"/>')
    for p in board.pads: lines.append(f'<rect x="{p.center.x-p.size_x/2}" y="{p.center.y-p.size_y/2}" width="{p.size_x}" height="{p.size_y}" fill="none" stroke="black"/>')
    lines.append('</svg>'); path.write_text("\n".join(lines)+"\n",encoding="utf-8"); return path
