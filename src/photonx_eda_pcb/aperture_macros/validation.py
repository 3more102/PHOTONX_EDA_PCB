def validate_macro(primitives):
    issues=[]
    for index,primitive in enumerate(primitives):
        if primitive.code not in {1,4,5,6,7,20,21}: issues.append(("warning","MACRO_PRIMITIVE_UNSUPPORTED",index,primitive.code))
        if not primitive.modifiers: issues.append(("error","MACRO_MODIFIERS_MISSING",index,primitive.code))
    return issues
