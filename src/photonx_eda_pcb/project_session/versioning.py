SESSION_SCHEMA_VERSION=1
def versioned_payload(payload):return {"schema_version":SESSION_SCHEMA_VERSION,"session":payload}
