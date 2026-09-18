from .model import KicadSchematic,KicadSymbol
def schematic_from_hypotheses(symbols,values=None,spacing_mm=25.4):
    values=values or {};out=KicadSchematic()
    for i,s in enumerate(symbols):
        ref=s.component_id
        out.symbols.append(KicadSymbol(ref,values.get(ref,"?"),s.library_id,(i%5)*spacing_mm,(i//5)*spacing_mm))
    return out
