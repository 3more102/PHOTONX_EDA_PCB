from .registry import RuleRegistry
from .id_rules import unique_object_ids
from .geometry_rules import positive_geometry
from .net_rules import valid_net_members
from .component_rules import valid_component_references
from .drill_rules import valid_drill_plating
from .outline_rules import outline_closed
from .provenance_rules import source_references_present
from .metadata_rules import metadata_sanity
def builtin_registry():
    r=RuleRegistry()
    for name,fn in [('ids',unique_object_ids),('geometry',positive_geometry),('nets',valid_net_members),('components',valid_component_references),('drills',valid_drill_plating),('outline',outline_closed),('provenance',source_references_present),('metadata',metadata_sanity)]: r.register(name,fn)
    return r
