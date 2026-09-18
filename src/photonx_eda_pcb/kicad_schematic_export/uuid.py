import uuid
_NAMESPACE=uuid.UUID("1a9274b2-1e11-5da5-9706-5248504f544f")
def stable_uuid(kind,*parts):
    return str(uuid.uuid5(_NAMESPACE,str(kind)+"|"+"|".join(map(str,parts))))
