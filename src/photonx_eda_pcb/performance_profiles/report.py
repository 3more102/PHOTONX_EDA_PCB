def performance_report(results):return [{"name":r.name,"median_seconds":r.median_seconds,"min_seconds":r.min_seconds,"max_seconds":r.max_seconds,"samples":len(r.samples)} for r in results]
