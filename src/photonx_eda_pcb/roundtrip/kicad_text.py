import re
def kicad_text_counts(text:str):
    return {'segments':len(re.findall(r'\(segment\s',text)),'footprints':len(re.findall(r'\(footprint\s',text)),'vias':len(re.findall(r'\(via\s',text)),'gr_lines':len(re.findall(r'\(gr_line\s',text))}
