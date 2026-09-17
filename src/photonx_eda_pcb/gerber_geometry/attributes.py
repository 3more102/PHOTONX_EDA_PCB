def object_function(attributes:dict):
    for key in ('.AperFunction','AperFunction','FileFunction'):
        if key in attributes:return attributes[key]
    return None
