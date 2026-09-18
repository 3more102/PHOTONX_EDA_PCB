from .status import checkpoint_status
def checkpoint_report(c):return {"id":c.id,"title":c.title,"status":checkpoint_status(c),"required_items":list(c.required_items),"decisions":[d.__dict__ for d in c.decisions]}
