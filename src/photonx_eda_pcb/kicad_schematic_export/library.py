from .escape import quote
def library_symbol_ids(doc):return tuple(sorted({s.library_id for s in doc.symbols}))
def write_lib_symbols(doc):
    lines=["  (lib_symbols"]
    for lib in library_symbol_ids(doc):
        ref=(lib.split(":")[-1][:1] or "U").upper()
        lines += [f"    (symbol {quote(lib)}",f"      (property {quote('Reference')} {quote(ref)} (at 0 2.54 0) (effects (font (size 1.27 1.27))))",f"      (property {quote('Value')} {quote(lib.split(':')[-1])} (at 0 0 0) (effects (font (size 1.27 1.27))))",f"      (property {quote('Footprint')} {quote('')} (at 0 0 0) (effects (font (size 1.27 1.27)) hide))",f"      (property {quote('Datasheet')} {quote('')} (at 0 0 0) (effects (font (size 1.27 1.27)) hide))","    )"]
    lines.append("  )");return lines
