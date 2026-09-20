def _group_rule(features,sig,prefix):
    sizes=features[f'{prefix}_group_sizes']
    expected_count=sig.get(f'{prefix}_group_count')
    expected_size=sig.get(f'{prefix}_group_size')
    if expected_count is not None and len(sizes)!=expected_count:
        return False
    if expected_size is not None and any(size!=expected_size for size in sizes):
        return False
    return True


def score_signature(features,sig):
    if features['count']!=sig.get('pad_count'):
        return 0.0

    drilled=features['drilled_fraction']
    if 'drilled_min' in sig and drilled<sig['drilled_min']:
        return 0.0
    if 'drilled_max' in sig and drilled>sig['drilled_max']:
        return 0.0
    if features['bbox_aspect']<sig.get('aspect_min',1.0):
        return 0.0
    if not _group_rule(features,sig,'primary'):
        return 0.0
    if not _group_rule(features,sig,'secondary'):
        return 0.0

    for axis in ('primary','secondary'):
        limit=sig.get(f'{axis}_pitch_cv_max')
        if limit is not None:
            observed=features.get(f'{axis}_pitch_cv')
            if observed is None or observed>limit:
                return 0.0

    area_limit=sig.get('pad_area_cv_max')
    if area_limit is not None:
        observed=features.get('pad_area_cv')
        if observed is None or observed>area_limit:
            return 0.0

    shape_min=sig.get('shape_uniformity_min')
    if shape_min is not None and features.get('shape_uniformity',0.0)<shape_min:
        return 0.0

    score=0.35
    if 'drilled_min' in sig or 'drilled_max' in sig:
        score+=0.20
    if 'aspect_min' in sig:
        score+=0.10
    if 'primary_group_count' in sig:
        score+=0.10
    if 'primary_group_size' in sig:
        score+=0.05
    if 'secondary_group_count' in sig:
        score+=0.10
    if 'secondary_group_size' in sig:
        score+=0.05
    if 'primary_pitch_cv_max' in sig or 'secondary_pitch_cv_max' in sig:
        score+=0.025
    if 'pad_area_cv_max' in sig:
        score+=0.025
    if 'shape_uniformity_min' in sig:
        score+=0.025
    return max(0.0,min(1.0,score))
