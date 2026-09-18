from .access import field_value
from .predicates import matches
def execute_query(items,query):
    return [x for x in items if matches(field_value(x,query.field),query.operator,query.value)]
