from dataclasses import dataclass
@dataclass(frozen=True)
class MechanicalExportReadiness:
    exportable_npth:tuple[str,...]
    unknown_plating:tuple[str,...]
    plated_without_padstack:tuple[str,...]
    @property
    def fully_resolved(self):return not self.unknown_plating and not self.plated_without_padstack

def assess_slot_export_readiness(slots):
    npth=[];unknown=[];plated=[]
    for s in slots:
        p=str(getattr(s,"plated","unknown")).lower().replace("_","-")
        if p=="non-plated":npth.append(s.id)
        elif p=="plated":plated.append(s.id)
        else:unknown.append(s.id)
    return MechanicalExportReadiness(tuple(sorted(npth)),tuple(sorted(unknown)),tuple(sorted(plated)))
