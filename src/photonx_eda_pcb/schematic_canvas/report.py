from .bounds import page_bounds
def canvas_report(doc,page_id):return {"page_id":str(page_id),"bounds":page_bounds(doc,page_id),"objects":len(doc.pages[str(page_id)].symbol_ids+doc.pages[str(page_id)].wire_ids+doc.pages[str(page_id)].label_ids+doc.pages[str(page_id)].bus_ids)}
