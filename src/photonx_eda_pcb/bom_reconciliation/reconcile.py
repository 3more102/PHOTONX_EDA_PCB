from .index import index_bom
from .normalize import normalize_reference,normalize_text
from .model import BomDiscrepancy
def reconcile_bom(bom_records,components):
    bom=index_bom(bom_records);seen=set();issues=[]
    for c in components:
        ref=normalize_reference(getattr(c,"reference",""))
        if not ref:continue
        seen.add(ref)
        if ref not in bom:issues.append(BomDiscrepancy(ref,"MISSING_FROM_BOM"))
        else:
            b=bom[ref]
            cv=normalize_text(getattr(c,"value",""))
            cf=normalize_text(getattr(c,"footprint",""))
            if cv and b.value and cv!=normalize_text(b.value):issues.append(BomDiscrepancy(ref,"VALUE_MISMATCH",b.value,getattr(c,"value","")))
            if cf and b.footprint and cf!=normalize_text(b.footprint):issues.append(BomDiscrepancy(ref,"FOOTPRINT_MISMATCH",b.footprint,getattr(c,"footprint","")))
    for ref in sorted(set(bom)-seen):issues.append(BomDiscrepancy(ref,"NOT_PLACED"))
    return sorted(issues,key=lambda x:(x.reference,x.code))
