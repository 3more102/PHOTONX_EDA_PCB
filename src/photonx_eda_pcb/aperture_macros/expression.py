import ast,operator
_OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.USub:operator.neg,ast.UAdd:operator.pos}
def eval_expr(text):
    node=ast.parse(str(text).replace("x","*").replace("X","*"),mode="eval").body
    def visit(n):
        if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)): return float(n.value)
        if isinstance(n,ast.UnaryOp) and type(n.op) in _OPS:return _OPS[type(n.op)](visit(n.operand))
        if isinstance(n,ast.BinOp) and type(n.op) in _OPS:return _OPS[type(n.op)](visit(n.left),visit(n.right))
        raise ValueError("unsupported macro expression")
    return visit(node)
