def length_group_report(items):return [x.__dict__.copy()|{"nets":list(x.nets)} for x in items]
