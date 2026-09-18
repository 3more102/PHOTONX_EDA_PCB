PROFILES={"small_grid":{"rows":10,"cols":10},"medium_grid":{"rows":30,"cols":30},"large_grid":{"rows":60,"cols":60},"clustered":{"clusters":20,"cluster_size":25}}
def profile(name):
    if name not in PROFILES:raise KeyError(name)
    return dict(PROFILES[name])
