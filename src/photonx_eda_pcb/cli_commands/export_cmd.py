from pathlib import Path
from .common import CommandResult
from ..validation_rules.export_rules import validate_export_path
def check_export_request(path:str|Path,kind:str):
    issues=validate_export_path(path,kind)
    return CommandResult(0,'export request checked',{'issues':[i.__dict__ for i in issues]})
