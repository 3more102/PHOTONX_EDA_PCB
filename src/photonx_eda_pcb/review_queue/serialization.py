from dataclasses import asdict
from .item import ReviewItem
def review_item_to_dict(item): return asdict(item)
def review_item_from_dict(value): return ReviewItem(**value)
