from .model import ArchitectureFinding,ArchitectureAudit
from .modules import package_file_collisions
from .names import duplicate_leaf_modules
from .capabilities import overlapping_capabilities
def audit_architecture(paths,capability_map=None):
    paths=list(paths);findings=[]
    for f,p in package_file_collisions(paths):findings.append(ArchitectureFinding("PACKAGE_FILE_COLLISION","error",f,f"collides with {p}"))
    for leaf,items in duplicate_leaf_modules(paths).items():
        if len(items)>=4:findings.append(ArchitectureFinding("REPEATED_MODULE_LEAF","info",leaf,f"{len(items)} modules share this leaf"))
    for cap,mods in overlapping_capabilities(capability_map or {}).items():
        if len(mods)>=3:findings.append(ArchitectureFinding("CAPABILITY_OVERLAP","warning",cap,", ".join(mods)))
    return ArchitectureAudit(findings,{"paths":len(paths),"findings":len(findings)})
