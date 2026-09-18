from .escape import quote,number
from .uuid import stable_uuid
from .library import write_lib_symbols

def _effects():
    return "(effects (font (size 1.27 1.27)))"

def write_export_document(doc):
    root=doc.root_uuid or stable_uuid("schematic",doc.project_name)
    lines=["(kicad_sch",f"  (version {int(doc.version)})","  (generator photonx)",f"  (uuid {root})",'  (paper "A4")']
    lines+=write_lib_symbols(doc)
    for s in sorted(doc.symbols,key=lambda x:(x.reference,x.id)):
        uid=stable_uuid("symbol",s.id,s.reference)
        lines += [
            "  (symbol",
            f"    (lib_id {quote(s.library_id)})",
            f"    (at {number(s.x)} {number(s.y)} {number(s.rotation)})",
            "    (unit 1)",
            "    (in_bom yes)",
            "    (on_board yes)",
            f"    (uuid {uid})",
            f"    (property {quote('Reference')} {quote(s.reference)} (at {number(s.x)} {number(s.y-2.54)} 0) {_effects()})",
            f"    (property {quote('Value')} {quote(s.value)} (at {number(s.x)} {number(s.y+2.54)} 0) {_effects()})",
            f"    (property {quote('Footprint')} {quote(s.footprint)} (at {number(s.x)} {number(s.y)} 0) {_effects()} hide)",
            "  )",
        ]
    for w in sorted(doc.wires,key=lambda x:x.id):
        pts=" ".join(f"(xy {number(x)} {number(y)})" for x,y in w.points)
        lines += [
            "  (wire",
            f"    (pts {pts})",
            "    (stroke (width 0) (type default))",
            f"    (uuid {stable_uuid('wire',w.id,w.net_id)})",
            "  )",
        ]
    for l in sorted(doc.labels,key=lambda x:x.id):
        token="global_label" if l.global_label else "label"
        extra=" (shape passive)" if l.global_label else ""
        lines += [f"  ({token} {quote(l.text)}{extra} (at {number(l.x)} {number(l.y)} 0) {_effects()} (uuid {stable_uuid('label',l.id,l.text)}))"]
    lines += ['  (sheet_instances (path "/" (page "1")))',")"]
    return "\n".join(lines)+"\n"
