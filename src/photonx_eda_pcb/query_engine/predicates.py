def matches(actual,op,expected):
    if op=="==":return actual==expected
    if op=="!=":return actual!=expected
    if op=="~":return str(expected).lower() in str(actual).lower()
    try:a=float(actual);e=float(expected)
    except (TypeError,ValueError):return False
    return {">":a>e,"<":a<e,">=":a>=e,"<=":a<=e}[op]
