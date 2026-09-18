from .types import edit_type_known
def validate_edit(op):
    issues=[]
    if not op.id.strip():issues.append("EDIT_ID_EMPTY")
    if not op.object_id.strip():issues.append("EDIT_OBJECT_EMPTY")
    if not edit_type_known(op.kind):issues.append("EDIT_KIND_UNKNOWN")
    return issues
