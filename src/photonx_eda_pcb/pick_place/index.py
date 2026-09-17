def by_reference(placements): return {placement.reference:placement for placement in sorted(placements,key=lambda item:item.reference)}
