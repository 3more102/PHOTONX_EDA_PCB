def current_margin(capacity_a,required_a):
    if capacity_a<=0:return -1.0
    return round((float(capacity_a)-float(required_a))/float(capacity_a),6)
