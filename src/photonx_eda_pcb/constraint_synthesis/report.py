def constraint_report(s):return [c.__dict__.copy()|{"evidence":list(c.evidence)} for c in s.constraints]
