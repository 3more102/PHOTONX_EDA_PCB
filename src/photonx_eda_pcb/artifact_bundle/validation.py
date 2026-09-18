from .hash import content_hash
def validate_bundle(bundle):
    issues=[];seen=set()
    for e in bundle.entries:
        if e.path in seen:issues.append("BUNDLE_DUPLICATE_PATH")
        seen.add(e.path)
        if content_hash(e.content)!=e.sha256:issues.append("BUNDLE_HASH_MISMATCH")
        if e.path.startswith("/") or ".." in e.path.replace("\\","/").split("/"):issues.append("BUNDLE_UNSAFE_PATH")
    return issues
