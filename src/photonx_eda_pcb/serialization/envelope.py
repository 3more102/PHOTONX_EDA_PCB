from datetime import datetime,timezone
def make_envelope(payload,schema_version="1.0",created_at=None):
    return {"schema_version":schema_version,"created_at":created_at or datetime.now(timezone.utc).isoformat(),"payload":payload}
