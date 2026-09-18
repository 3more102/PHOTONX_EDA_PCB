def governance_report(items):return [{"name":x.name,"passed":x.passed,"blockers":list(x.blockers),"evidence":x.evidence or {}} for x in items]
