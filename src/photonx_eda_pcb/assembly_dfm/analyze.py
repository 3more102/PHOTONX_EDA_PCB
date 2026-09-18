from .model import AssemblyFinding,AssemblyDfmReport
from .edge_clearance import component_edge_clearance
from .polarity import requires_polarity_mark
def analyze_assembly_dfm(components,board_bounds,*,min_edge_mm=.5,polarity_marked=()):
    marked=set(map(str,polarity_marked));f=[];edge_values=[]
    for c in components:
        ref=str(getattr(c,"reference",""));clr=component_edge_clearance(getattr(c,"center"),board_bounds);edge_values.append(clr)
        if clr<float(min_edge_mm):f.append(AssemblyFinding("COMPONENT_EDGE_CLEARANCE","warning",ref,f"{clr:.3f} mm"))
        if requires_polarity_mark(getattr(c,"kind","")) and ref not in marked:f.append(AssemblyFinding("POLARITY_MARK_MISSING","warning",ref,""))
    return AssemblyDfmReport(f,{"components":len(list(components)),"min_edge_clearance_mm":min(edge_values) if edge_values else 0.0})
