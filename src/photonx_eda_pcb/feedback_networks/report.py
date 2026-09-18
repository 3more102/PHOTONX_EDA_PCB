def feedback_summary(items):return {"candidates":len(items),"components":sorted({c for x in items for c in x.components})}
