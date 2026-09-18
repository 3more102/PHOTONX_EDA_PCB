from .catalog import DiagnosticCatalog
from .model import DiagnosticDefinition
def default_catalog():
    c=DiagnosticCatalog()
    for x in [
      DiagnosticDefinition("UNSUPPORTED_SYNTAX","critical","Unsupported manufacturing syntax","Input contains constructs not interpreted by the parser.","Add parser support or review with a trusted CAM tool."),
      DiagnosticDefinition("CONNECTIVITY_CONFLICT","error","Connectivity conflict","Independent evidence sources disagree about electrical connectivity.","Inspect geometry, via span and source net evidence."),
      DiagnosticDefinition("UNRESOLVED_COMPONENT","warning","Unresolved component","A component candidate cannot be classified with sufficient evidence.","Review footprint geometry, silkscreen and BOM evidence."),
      DiagnosticDefinition("LOW_CONFIDENCE","warning","Low-confidence inference","Inference confidence is below the review threshold.","Add independent evidence or keep as unresolved."),
      DiagnosticDefinition("PROVENANCE_MISSING","error","Missing provenance","A derived object lacks traceable source evidence.","Repair evidence/provenance links before release."),
    ]:c.add(x)
    return c
