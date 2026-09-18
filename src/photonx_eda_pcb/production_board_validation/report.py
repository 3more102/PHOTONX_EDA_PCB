def production_validation_report(r):return {"passed":r.passed,"blockers":list(r.blockers),"warnings":list(r.warnings),"metrics":dict(r.metrics)}
