from .ast import MacroVariableDefinition
from .primitives import SUPPORTED


def validate_macro(primitives):
    issues = []
    for index, primitive in enumerate(primitives):
        if isinstance(primitive, MacroVariableDefinition):
            continue
        if primitive.code not in SUPPORTED:
            issues.append(
                ("warning", "MACRO_PRIMITIVE_UNSUPPORTED", index, primitive.code)
            )
        if not primitive.modifiers:
            issues.append(
                ("error", "MACRO_MODIFIERS_MISSING", index, primitive.code)
            )
    return issues
