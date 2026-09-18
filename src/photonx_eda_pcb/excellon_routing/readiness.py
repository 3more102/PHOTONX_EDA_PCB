from dataclasses import dataclass
@dataclass(frozen=True)
class RouteExportReadiness:
    exportable:tuple[str,...]
    omitted:tuple[str,...]
    reasons:dict[str,str]
    @property
    def fully_resolved(self):return not self.omitted

def assess_route_export_readiness(routes):
    # Arbitrary routed milling cannot be represented faithfully as a single KiCad pad.
    # Keep routes explicit and omitted until an export target with equivalent semantics exists.
    omitted=tuple(sorted(r.id for r in routes))
    return RouteExportReadiness((),omitted,{r.id:"KICAD_ARBITRARY_ROUTE_UNSUPPORTED" for r in routes})
