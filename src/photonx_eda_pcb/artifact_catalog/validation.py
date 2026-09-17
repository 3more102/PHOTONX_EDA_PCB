from .checksums import valid_sha256
from .lineage import missing_dependencies
def validate_catalog(catalog):
    issues=[]
    for name in catalog.names():
        a=catalog.get(name)
        if a.sha256 is not None and not valid_sha256(a.sha256):issues.append({'severity':'error','code':'ARTIFACT_HASH_INVALID','artifact':name})
        if not a.path:issues.append({'severity':'error','code':'ARTIFACT_PATH_EMPTY','artifact':name})
    for dep in missing_dependencies(catalog):issues.append({'severity':'warning','code':'ARTIFACT_INPUT_MISSING','artifact':dep})
    return issues
