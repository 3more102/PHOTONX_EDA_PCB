from .quality import layout_quality
def autolayout_report(result):return {"page_id":result.page_id,"positions":dict(result.positions),"routes":len(result.routes),"quality":layout_quality(result)}
