def artifact_manifest(project):
    return [{"role":a.role,"path":a.path,"sha256":a.sha256,"required":a.required} for a in sorted(project.artifacts,key=lambda x:(x.role,x.path))]
