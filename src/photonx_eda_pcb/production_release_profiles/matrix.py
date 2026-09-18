from .evaluate import evaluate_release_profile
def evaluate_all(profiles,evidence):return [evaluate_release_profile(p,evidence) for p in profiles]
