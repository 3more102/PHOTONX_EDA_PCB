import json
from .summary import build_summary
def render_json_report(board,indent:int=2)->str: return json.dumps(build_summary(board),indent=indent,sort_keys=True)+"\n"
