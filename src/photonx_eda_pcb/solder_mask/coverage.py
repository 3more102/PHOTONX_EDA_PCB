def opening_area(opening):
    return float(opening.size[0])*float(opening.size[1])
def total_open_area(openings):
    return sum(opening_area(o) for o in openings)
