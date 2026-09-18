def pair_report(pairs):
    return [{"p":p.positive_net,"n":p.negative_net,"confidence":p.confidence,"reasons":list(p.reasons)} for p in pairs]
