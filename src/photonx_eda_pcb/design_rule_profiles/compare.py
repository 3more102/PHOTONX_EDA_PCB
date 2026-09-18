from .resolve import resolve_profile
def compare_profiles(a,b):
    ra,rb=resolve_profile(a),resolve_profile(b)
    return {k:(ra[k],rb[k]) for k in sorted(ra) if ra[k]!=rb[k]}
