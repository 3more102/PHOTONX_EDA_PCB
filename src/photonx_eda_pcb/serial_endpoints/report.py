def serial_report(items):return [{"protocol":x.protocol,"nets":list(x.nets),"confidence":x.confidence,"endpoints":[e.__dict__ for e in x.endpoints],"evidence":list(x.evidence)} for x in items]
