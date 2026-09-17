from .ids import check_unique_object_ids
from .geometry import check_geometry
from .nets import check_nets
from .components import check_components
from .drills import check_drills
from .outline import check_outline
from .metadata import check_metadata
from .provenance import check_provenance
def run_all_checks(board):
    issues=[]
    for fn in (check_unique_object_ids,check_geometry,check_nets,check_components,check_drills,check_outline,check_metadata,check_provenance): issues.extend(fn(board))
    return issues
