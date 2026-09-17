SUPPORTED_MAJOR={1}
def parse_version(text): return tuple(int(part) for part in str(text).split("."))
def require_supported(text):
    version=parse_version(text)
    if not version or version[0] not in SUPPORTED_MAJOR: raise ValueError(f"unsupported schema version: {text}")
    return version
