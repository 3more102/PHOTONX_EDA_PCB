from .model import FabricationRules
DEFAULT_RULES=FabricationRules()
CONSERVATIVE_RULES=FabricationRules(min_track_mm=0.2,min_clearance_mm=0.2,min_drill_mm=0.3,min_annular_mm=0.125)
