def validate_export_document(doc):
    issues=[];refs=set();ids=set()
    if not doc.project_name.strip():issues.append("KICAD_EXPORT_PROJECT_EMPTY")
    if not doc.root_uuid:issues.append("KICAD_EXPORT_ROOT_UUID_EMPTY")
    for s in doc.symbols:
        if s.reference in refs:issues.append("KICAD_EXPORT_DUPLICATE_REFERENCE")
        refs.add(s.reference)
        if s.id in ids:issues.append("KICAD_EXPORT_DUPLICATE_ID")
        ids.add(s.id)
        if not s.library_id:issues.append("KICAD_EXPORT_LIBRARY_ID_EMPTY")
    for w in doc.wires:
        if len(w.points)<2:issues.append("KICAD_EXPORT_WIRE_TOO_SHORT")
    return issues
