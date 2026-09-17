def clamp(value:float, low:float, high:float)->float:
    if low>high: raise ValueError("low must be <= high")
    return max(low,min(high,value))
def in_closed_range(value:float, low:float, high:float)->bool: return low<=value<=high
