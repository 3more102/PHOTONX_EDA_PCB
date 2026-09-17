from __future__ import annotations
import argparse, json
from pathlib import Path
from .project import load_project
from .kicad import export_kicad

def main():
    ap=argparse.ArgumentParser(prog='photonx',description='PHOTONX EDA PCB reverse-engineering MVP')
    ap.add_argument('input_dir'); ap.add_argument('--gui',action='store_true'); ap.add_argument('--json'); ap.add_argument('--kicad')
    args=ap.parse_args(); board=load_project(args.input_dir)
    print(f'PHOTONX: {len(board.pads)} pads, {len(board.tracks)} tracks, {len(board.nets)} nets, {len(board.components)} component hypotheses')
    if args.json: Path(args.json).write_text(json.dumps(board.to_dict(),indent=2),encoding='utf-8')
    if args.kicad: print(export_kicad(board,args.kicad))
    if args.gui:
        from .gui import show; show(board)
if __name__=='__main__': main()
