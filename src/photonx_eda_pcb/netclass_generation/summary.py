def netclass_summary(items):return {"classes":len(items),"nets":sum(len(x.nets) for x in items)}
