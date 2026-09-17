from .lexer import lex
def parse_sexpr(text:str):
    toks=lex(text); pos=0
    def parse_one():
        nonlocal pos
        if pos>=len(toks): raise ValueError('unexpected eof')
        t=toks[pos]; pos+=1
        if t=='(':
            arr=[]
            while pos<len(toks) and toks[pos]!=')': arr.append(parse_one())
            if pos>=len(toks): raise ValueError('missing )')
            pos+=1; return arr
        if t==')': raise ValueError('unexpected )')
        kind,val=t
        if kind=='str': return val
        try:return int(val)
        except ValueError:
            try:return float(val)
            except ValueError:return val
    root=parse_one()
    if pos!=len(toks): raise ValueError('trailing tokens')
    return root
