def filter_eco(eco,*,category=None,action=None,approved=None):
    return [x for x in eco.changes if (category is None or x.category==category) and (action is None or x.action==action) and (approved is None or x.approved==approved)]
