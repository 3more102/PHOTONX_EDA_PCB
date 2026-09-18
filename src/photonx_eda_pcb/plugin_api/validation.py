from .capabilities import validate_capabilities
def validate_plugin(plugin):
    issues=[];m=getattr(plugin,"metadata",None)
    if m is None:return ["PLUGIN_METADATA_MISSING"]
    if not m.name.strip():issues.append("PLUGIN_NAME_EMPTY")
    if int(m.api_version)!=1:issues.append("PLUGIN_API_VERSION_UNSUPPORTED")
    if validate_capabilities(m.capabilities):issues.append("PLUGIN_UNKNOWN_CAPABILITY")
    return issues
