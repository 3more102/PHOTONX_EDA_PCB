from .model import ErcIssue
from ..schematic.topology import dangling_nets
def check_dangling(board): return [ErcIssue('warning','DANGLING_NET',f'net {n} reaches one or zero component hypotheses',n) for n in dangling_nets(board)]
