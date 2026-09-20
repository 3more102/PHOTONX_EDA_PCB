SIGNATURES=[
    {
        'name':'TWO_PIN_THT',
        'pad_count':2,
        'drilled_min':0.9,
        'aspect_min':1.2,
        'pad_area_cv_max':0.35,
    },
    {
        'name':'TWO_PAD_SMD',
        'pad_count':2,
        'drilled_max':0.1,
        'aspect_min':1.2,
        'pad_area_cv_max':0.35,
    },
    {
        'name':'SOIC8_LIKE',
        'pad_count':8,
        'drilled_max':0.1,
        'aspect_min':1.2,
        'primary_group_count':2,
        'primary_group_size':4,
        'secondary_group_count':4,
        'secondary_group_size':2,
        'secondary_pitch_cv_max':0.15,
        'pad_area_cv_max':0.20,
        'shape_uniformity_min':0.75,
    },
    {
        'name':'DIP8_LIKE',
        'pad_count':8,
        'drilled_min':0.8,
        'aspect_min':1.2,
        'primary_group_count':2,
        'primary_group_size':4,
        'secondary_group_count':4,
        'secondary_group_size':2,
        'secondary_pitch_cv_max':0.15,
        'pad_area_cv_max':0.20,
        'shape_uniformity_min':0.75,
    },
]


def signature_by_name(name):
    return next((item for item in SIGNATURES if item['name']==name),None)
