import json
from pathlib import Path
def dump_json(data,path:str|Path)->Path:
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8"); return path
def load_json(path:str|Path): return json.loads(Path(path).read_text(encoding="utf-8"))
