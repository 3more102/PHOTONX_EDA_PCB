from pathlib import Path
def inventory(root:str|Path)->list[dict[str,object]]:
    root=Path(root); out=[]
    for p in sorted(x for x in root.rglob("*") if x.is_file()): out.append({"path":p.relative_to(root).as_posix(),"size":p.stat().st_size,"suffix":p.suffix.lower()})
    return out
