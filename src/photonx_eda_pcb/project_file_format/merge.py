from copy import deepcopy
def merge_projects(base,overlay):
    out=deepcopy(base)
    by={(a.role,a.path):a for a in out.artifacts}
    for a in overlay.artifacts:by[(a.role,a.path)]=a
    out.artifacts=[by[k] for k in sorted(by)]
    out.settings.update(overlay.settings);out.metadata.update(overlay.metadata)
    out.schema_version=max(out.schema_version,overlay.schema_version)
    return out
