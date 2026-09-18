from .hash import payload_hash
def validate_snapshot(s):
    issues=[]
    if payload_hash(s.payload)!=s.sha256:issues.append("SNAPSHOT_HASH_MISMATCH")
    if not s.id.strip():issues.append("SNAPSHOT_EMPTY_ID")
    return issues
