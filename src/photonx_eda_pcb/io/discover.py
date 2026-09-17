from pathlib import Path
GERBER_SUFFIXES={".gbr",".ger",".gtl",".gbl",".gto",".gbo",".gm1"}; DRILL_SUFFIXES={".drl",".xln",".exc"}
def discover_manufacturing_files(root:str|Path)->dict[str,list[Path]]:
    files=[p for p in Path(root).rglob("*") if p.is_file()]
    return {"gerber":sorted([p for p in files if p.suffix.lower() in GERBER_SUFFIXES]),"drill":sorted([p for p in files if p.suffix.lower() in DRILL_SUFFIXES]),"other":sorted([p for p in files if p.suffix.lower() not in GERBER_SUFFIXES|DRILL_SUFFIXES])}
