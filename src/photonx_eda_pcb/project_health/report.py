from .grade import health_grade
def health_report(h):return {"score":h.score,"grade":health_grade(h.score),"metrics":[{"name":m.name,"score":m.score,"weight":m.weight,"details":m.details} for m in h.metrics]}
