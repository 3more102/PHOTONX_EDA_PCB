def comparison_summary(brute,spatial):
    ratio=None if brute.median_seconds<=0 else spatial.median_seconds/brute.median_seconds
    return {"bruteforce_seconds":brute.median_seconds,"spatial_seconds":spatial.median_seconds,"spatial_to_bruteforce_ratio":ratio,"spatial_faster":None if ratio is None else ratio<1.0}
