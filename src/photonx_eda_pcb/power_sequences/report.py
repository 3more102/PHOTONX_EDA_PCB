def sequence_report(items):return [{"before":x.before,"after":x.after,"reason":x.reason,"confidence":x.confidence,"evidence":list(x.evidence)} for x in items]
