from .model import RoutedPath,RouteSegment
from .geometry import route_shape
from .validation import validate_route

_READINESS_EXPORTS={
    "assess_route_export_readiness",
    "is_exact_npth_slot_route",
    "route_export_descriptor",
}

def __getattr__(name):
    if name in _READINESS_EXPORTS:
        from . import readiness as _readiness
        value=getattr(_readiness,name)
        globals()[name]=value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__=[
    "RoutedPath",
    "RouteSegment",
    "route_shape",
    "validate_route",
    "assess_route_export_readiness",
    "is_exact_npth_slot_route",
    "route_export_descriptor",
]
