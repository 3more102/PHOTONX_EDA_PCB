ALIASES={'F.Cu':'top_copper','B.Cu':'bottom_copper','Edge.Cuts':'outline','F.Mask':'top_mask','B.Mask':'bottom_mask','F.SilkS':'top_silkscreen','B.SilkS':'bottom_silkscreen'}
def role_for_layer(name:str)->str:
    if name in ALIASES:return ALIASES[name]
    if name.startswith('In') and name.endswith('.Cu'): return 'inner_copper'
    return 'unknown'
def is_copper(name:str)->bool: return name.endswith('.Cu')
