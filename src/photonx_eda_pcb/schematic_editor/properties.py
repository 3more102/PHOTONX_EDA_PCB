from dataclasses import replace
def set_symbol_properties(doc,symbol_id,**changes):
    allowed={"reference","value","library_id","confidence","rotation"}
    bad=set(changes)-allowed
    if bad:raise ValueError(f"unsupported symbol properties: {sorted(bad)}")
    s=doc.symbols[symbol_id];n=replace(s,**changes);doc.symbols[symbol_id]=n;return n
