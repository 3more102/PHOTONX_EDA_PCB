def validate_fuse(f):
    return [] if 0<=f.confidence<=1 else ["FUSE_CONFIDENCE_RANGE"]
