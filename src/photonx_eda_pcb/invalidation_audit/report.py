def invalidation_report(results):return [{"passed":r.passed,"planned":list(r.planned),"missing":list(r.missing),"unexpected":list(r.unexpected)} for r in results]
