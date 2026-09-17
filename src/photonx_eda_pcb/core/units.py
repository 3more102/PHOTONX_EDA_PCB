MM_PER_INCH=25.4
def mm_to_um(mm:float)->int: return round(mm*1000)
def um_to_mm(um:int|float)->float: return float(um)/1000.0
def inch_to_mm(inch:float)->float: return inch*MM_PER_INCH
def mil_to_mm(mil:float)->float: return inch_to_mm(mil/1000.0)
