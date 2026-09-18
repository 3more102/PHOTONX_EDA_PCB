def pad_per_component(stats):return None if stats.components==0 else round(stats.pads/stats.components,6)
def drills_per_pad(stats):return None if stats.pads==0 else round(stats.drills/stats.pads,6)
