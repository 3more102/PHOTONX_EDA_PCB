def netclass_report(items):
    return [{"net_id":x.net_id,"class":x.class_name,"confidence":x.confidence,"evidence":list(x.evidence)} for x in items]
