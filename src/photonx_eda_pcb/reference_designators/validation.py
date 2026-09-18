from .normalize import normalize_reference
def validate_reference(ref):
    return [] if normalize_reference(ref) else ["REFERENCE_INVALID"]
