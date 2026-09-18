from .model import ExportDocument,ExportSymbol,ExportWire,ExportLabel
from .uuid import stable_uuid
def export_document_from_editor(doc,project_name="PHOTONX"):
    root=stable_uuid("schematic",project_name)
    out=ExportDocument(str(project_name),root)
    for s in sorted(doc.symbols.values(),key=lambda x:(x.reference,x.id)):
        out.symbols.append(ExportSymbol(s.id,s.library_id,s.reference,s.value,s.x,s.y,s.rotation,""))
    for w in sorted(doc.wires.values(),key=lambda x:x.id):out.wires.append(ExportWire(w.id,w.net_id,w.points))
    for l in sorted(doc.labels.values(),key=lambda x:x.id):out.labels.append(ExportLabel(l.id,l.text,l.x,l.y,l.global_label))
    return out
