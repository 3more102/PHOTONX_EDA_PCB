def lex(text:str):
    out=[]; i=0
    while i<len(text):
        c=text[i]
        if c.isspace(): i+=1; continue
        if c in '()': out.append(c); i+=1; continue
        if c=='"':
            j=i+1; buf=[]
            while j<len(text) and text[j]!='"':
                if text[j]=='\\' and j+1<len(text): j+=1; buf.append(text[j])
                else: buf.append(text[j])
                j+=1
            if j>=len(text): raise ValueError('unterminated string')
            out.append(('str',''.join(buf))); i=j+1; continue
        j=i
        while j<len(text) and not text[j].isspace() and text[j] not in '()': j+=1
        out.append(('atom',text[i:j])); i=j
    return out
