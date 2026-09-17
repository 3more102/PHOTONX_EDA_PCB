from __future__ import annotations
import re
from pathlib import Path
from .models import Point, Track, Pad, Outline

AD_RE = re.compile(r"%ADD(\d+)([CRO]),?([0-9.]+)(?:X([0-9.]+))?\*%")
FS_RE = re.compile(r"%FSLAX(\d)(\d)Y(\d)(\d)\*%")
COORD_RE = re.compile(r"(?:X(-?[0-9.]+))?(?:Y(-?[0-9.]+))?(?:D0?([123]))?\*")
SEL_RE = re.compile(r"D(\d+)\*")

class GerberParser:
    """Small RS-274X subset parser supporting apertures, moves, draws and flashes."""
    def __init__(self, layer: str = "F.Cu"):
        self.layer = layer
        self.apertures: dict[int, tuple[str,float,float|None]] = {}
        self.fs = (2,4,2,4)

    def _num(self, raw: str | None, axis: str) -> float | None:
        if raw is None:
            return None
        if "." in raw:
            return float(raw)
        neg = raw.startswith("-")
        s = raw[1:] if neg else raw
        dec = self.fs[1] if axis == "x" else self.fs[3]
        val = int(s) / (10**dec)
        return -val if neg else val

    def parse(self, path: str | Path):
        lines = Path(path).read_text(encoding="utf-8", errors="ignore").splitlines()
        tracks, pads = [], []
        cur = Point(0.0,0.0)
        ap = None
        tid = pid = 0
        for rawline in lines:
            line = rawline.strip()
            m=FS_RE.match(line)
            if m:
                self.fs = tuple(map(int,m.groups())); continue
            m=AD_RE.match(line)
            if m:
                code=int(m.group(1)); shape=m.group(2); a=float(m.group(3)); b=float(m.group(4)) if m.group(4) else None
                self.apertures[code]=(shape,a,b); continue
            m=SEL_RE.fullmatch(line)
            if m and int(m.group(1)) >= 10:
                ap=int(m.group(1)); continue
            m=COORD_RE.fullmatch(line)
            if not m: continue
            x=self._num(m.group(1),'x'); y=self._num(m.group(2),'y'); op=m.group(3)
            nxt=Point(cur.x if x is None else x, cur.y if y is None else y)
            if op == '1' and ap in self.apertures:
                width=self.apertures[ap][1]
                tracks.append(Track(f"T{tid}",cur,nxt,width,self.layer)); tid+=1
            elif op == '3' and ap in self.apertures:
                shape,a,b=self.apertures[ap]
                diameter=max(a,b or a)
                pads.append(Pad(f"P{pid}",nxt,diameter,self.layer)); pid+=1
            cur=nxt
        return tracks,pads


def parse_outline(path: str | Path) -> Outline:
    tracks,_ = GerberParser("Edge.Cuts").parse(path)
    return Outline(tracks)
