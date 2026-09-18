def release_summary(m):return {"version":m.version,"commit":m.commit,"artifacts":len(m.artifacts),"bytes":sum(a.size for a in m.artifacts)}
