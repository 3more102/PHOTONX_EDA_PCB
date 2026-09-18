def merge_small_blocks(blocks,min_components=2):
    large=[b for b in blocks if len(b.components)>=min_components]
    small=[b for b in blocks if len(b.components)<min_components]
    return large,small
