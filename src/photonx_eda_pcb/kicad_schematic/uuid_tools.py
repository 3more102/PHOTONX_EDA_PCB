import uuid
def stable_uuid(namespace,name):
    ns=uuid.UUID(str(namespace)) if namespace else uuid.NAMESPACE_URL
    return str(uuid.uuid5(ns,str(name)))
