from __future__ import annotations
import re
from pathlib import Path
from .models import Point, Hole

TOOL_RE = re.compile(r"T(\d+)C([0-9.]+)")
SEL_RE = re.compile(r"T(\d+)$")
XY_RE = re.compile(r"X(-?[0-9.]+)Y(-?[0-9.]+)")


def parse_excellon(path: str | Path) -> list[Hole]:
    tools: dict[int,float] = {}
    current=None
    holes=[]
    hid=0
    for raw in Path(path).read_text(encoding='utf-8',errors='ignore').splitlines():
        line=raw.strip().upper()
        m=TOOL_RE.fullmatch(line)
        if m:
            tools[int(m.group(1))]=float(m.group(2)); continue
        m=SEL_RE.fullmatch(line)
        if m:
            current=int(m.group(1)); continue
        m=XY_RE.fullmatch(line)
        if m and current in tools:
            holes.append(Hole(f"H{hid}",Point(float(m.group(1)),float(m.group(2))),tools[current],True)); hid+=1
    return holes
