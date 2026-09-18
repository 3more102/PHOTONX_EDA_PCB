from .model import PackageAssessment
def assess_package(artifacts,requirements,omissions=()):
    counts={}
    for a in artifacts:
        role=str(getattr(a,"role",getattr(a,"kind","unknown"))).lower()
        counts[role]=counts.get(role,0)+1
    missing=[];blockers=[];warnings=[]
    for r in requirements:
        have=counts.get(r.role.lower(),0)
        if have<r.minimum:
            missing.append(r.role)
            (blockers if r.required else warnings).append("PACKAGE_MISSING_"+r.role.upper())
    for o in omissions:
        code=str(getattr(o,"code",o.get("code","") if isinstance(o,dict) else ""))
        sev=str(getattr(o,"severity",o.get("severity","warning") if isinstance(o,dict) else "warning"))
        if code:
            (blockers if sev=="error" else warnings).append("OMISSION_"+code)
    return PackageAssessment(dict(sorted(counts.items())),sorted(missing),sorted(set(blockers)),sorted(set(warnings)))
