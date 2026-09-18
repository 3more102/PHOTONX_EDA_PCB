def page_set_report(ps):return {"pages":len(ps.pages),"items":[{"id":p.id,"title":p.title,"block_kind":p.block_kind,"components":len(p.components),"nets":len(p.nets)} for p in ps.pages]}
