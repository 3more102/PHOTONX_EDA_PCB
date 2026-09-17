import os,tempfile
from pathlib import Path
def atomic_write_text(path:str|Path,text:str)->Path:
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=path.name+".",text=True)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f: f.write(text)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    return path
