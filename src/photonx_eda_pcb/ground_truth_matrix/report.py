def results_report(results):return [{"id":r.id,"passed":r.passed,"mismatches":list(r.mismatches)} for r in results]
