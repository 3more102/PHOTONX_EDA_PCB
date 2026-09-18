def paste_confidence(has_smd_pad=True,has_source_paste=False):
    return round(min((0.6 if has_smd_pad else 0)+(0.4 if has_source_paste else 0),1.0),12)
