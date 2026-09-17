from .dangling import check_dangling
from .components import check_components
from .net_labels import check_labels
from .unresolved import check_unresolved_pins
RULES=(check_dangling,check_components,check_labels,check_unresolved_pins)
def run_erc(board):
    out=[]
    for r in RULES:out.extend(r(board))
    return out
