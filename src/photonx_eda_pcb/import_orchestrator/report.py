def import_report(results):return [{"path":r.path,"success":r.success,"format":r.format,"diagnostics":list(r.diagnostics)} for r in results]
