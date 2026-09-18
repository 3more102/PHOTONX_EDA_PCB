def pattern_match_report(items):return [{"pattern":x.pattern,"object_id":x.object_id,"score":x.score,"evidence":list(x.evidence)} for x in items]
