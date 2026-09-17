from .model import ErcIssue
from ..schematic.netlist import unresolved_component_pins
def check_unresolved_pins(board): return [ErcIssue('warning','PIN_NET_UNKNOWN',f'unresolved pin indices {pins}',cid) for cid,pins in unresolved_component_pins(board).items()]
