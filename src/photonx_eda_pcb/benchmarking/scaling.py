def normalize_per_object(seconds,count):return None if count<=0 else seconds/count
def speedup(baseline_seconds,current_seconds):return float('inf') if current_seconds==0 else baseline_seconds/current_seconds
def percent_change(baseline,current):return 0.0 if baseline==0 and current==0 else (float('inf') if baseline==0 else (current-baseline)/baseline*100.0)
