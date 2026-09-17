from pathlib import Path
from .base import RuleIssue
def validate_export_path(path:str|Path,kind:str):
    suffix=Path(path).suffix.lower(); expected={'json':'.json','kicad':'.kicad_pcb','svg':'.svg','graphml':'.graphml','csv':'.csv'}.get(kind)
    if expected and suffix!=expected: return [RuleIssue('warning','EXPORT_SUFFIX',f'expected {expected}, got {suffix or "<none>"}')]
    return []
