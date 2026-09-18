def learned_profile_report(p):return {"name":p.name,"rules":{k:{"value":r.value,"confidence":r.confidence,"sample_count":r.sample_count} for k,r in sorted(p.rules.items())}}
