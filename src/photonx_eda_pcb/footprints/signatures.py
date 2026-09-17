SIGNATURES=[
 {'name':'TWO_PIN_THT','pad_count':2,'drilled_min':0.9,'aspect_min':1.2},
 {'name':'TWO_PAD_SMD','pad_count':2,'drilled_max':0.1,'aspect_min':1.2},
 {'name':'SOIC8_LIKE','pad_count':8,'drilled_max':0.1,'aspect_min':1.2},
 {'name':'DIP8_LIKE','pad_count':8,'drilled_min':0.8,'aspect_min':1.2},
]
def signature_by_name(name): return next((x for x in SIGNATURES if x['name']==name),None)
