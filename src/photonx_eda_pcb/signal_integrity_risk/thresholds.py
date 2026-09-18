DEFAULT_THRESHOLDS={"low":.0,"medium":.4,"high":.75}
def exceeds(score,level):return float(score)>=DEFAULT_THRESHOLDS[level]
