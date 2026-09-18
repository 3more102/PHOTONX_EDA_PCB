def export_summary(doc):return {"project":doc.project_name,"symbols":len(doc.symbols),"wires":len(doc.wires),"labels":len(doc.labels),"version":doc.version}
