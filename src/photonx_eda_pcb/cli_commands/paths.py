from pathlib import Path
def require_existing_directory(value:str|Path)->Path:
    p=Path(value)
    if not p.exists() or not p.is_dir(): raise ValueError(f'not a directory: {p}')
    return p
def output_path(value:str|Path)->Path:
    p=Path(value); p.parent.mkdir(parents=True,exist_ok=True); return p
