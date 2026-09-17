from .expression import eval_expr
from .primitives import primitive_name
from .variables import substitute
def evaluate_macro(primitives,variables=None):
    variables=variables or {}
    out=[]
    for primitive in primitives:
        values=[eval_expr(substitute(x,variables)) for x in primitive.modifiers]
        out.append({"code":primitive.code,"kind":primitive_name(primitive.code),"values":values})
    return out
