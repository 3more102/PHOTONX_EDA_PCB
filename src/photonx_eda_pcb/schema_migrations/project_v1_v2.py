def project_v1_to_v2(payload):
    p=dict(payload)
    p.setdefault("metadata",{})
    p.setdefault("settings",{})
    arts=[]
    for a in p.get("artifacts",[]):
        x=dict(a);x.setdefault("sha256","");x.setdefault("required",False);arts.append(x)
    p["artifacts"]=arts
    p["schema_version"]=2
    return p
