from .model import PackageRequirement
def pcb_fabrication_profile():
    return [PackageRequirement("copper",1),PackageRequirement("outline",1),PackageRequirement("drill",1),PackageRequirement("solder_mask",1,False),PackageRequirement("silkscreen",1,False),PackageRequirement("bom",1,False),PackageRequirement("pick_place",1,False),PackageRequirement("report",1,False)]
