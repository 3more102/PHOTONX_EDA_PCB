KNOWN_KINDS={'source','normalized_geometry','board_model','connectivity','report','kicad','json','csv','svg','graphml','manifest','log'}
def normalize_kind(value):return str(value).strip().lower().replace(' ','_')
def known_kind(value):return normalize_kind(value) in KNOWN_KINDS
