from .ast import MacroVariableDefinition
from .primitives import is_supported_primitive


def validate_macro(primitives):
    issues = []
    for index, primitive in enumerate(primitives):
        if isinstance(primitive, MacroVariableDefinition):
            continue
        if not is_supported_primitive(primitive.code):
            issues.append(
                ("warning", "MACRO_PRIMITIVE_UNSUPPORTED", index, primitive.code)
            )
        if not primitive.modifiers:
            issues.append(
                ("error", "MACRO_MODIFIERS_MISSING", index, primitive.code)
            )
    return issues
