import ast
import operator
from math import isfinite


_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _number(value, *, reject_nonfinite):
    if isinstance(value, bool):
        raise ValueError("unsupported macro expression")
    result = float(value)
    if reject_nonfinite and not isfinite(result):
        raise ValueError("non-finite macro expression")
    return result


def eval_expr(text, *, reject_nonfinite=True):
    node = ast.parse(str(text).replace("x", "*").replace("X", "*"), mode="eval").body

    def visit(current):
        if isinstance(current, ast.Constant) and isinstance(
            current.value, (int, float)
        ):
            return _number(current.value, reject_nonfinite=reject_nonfinite)
        if isinstance(current, ast.UnaryOp) and type(current.op) in _OPS:
            return _number(
                _OPS[type(current.op)](visit(current.operand)),
                reject_nonfinite=reject_nonfinite,
            )
        if isinstance(current, ast.BinOp) and type(current.op) in _OPS:
            return _number(
                _OPS[type(current.op)](visit(current.left), visit(current.right)),
                reject_nonfinite=reject_nonfinite,
            )
        raise ValueError("unsupported macro expression")

    return visit(node)
