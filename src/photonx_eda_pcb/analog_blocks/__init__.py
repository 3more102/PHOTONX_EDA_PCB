from .model import AnalogBlockCandidate
from .validation import validate_analog_block

def detect_analog_blocks(*args, **kwargs):
    # Lazy import prevents circular initialization with detector subpackages
    # that depend on analog_blocks.model.
    from .detect import detect_analog_blocks as _detect
    return _detect(*args, **kwargs)

__all__=["AnalogBlockCandidate","detect_analog_blocks","validate_analog_block"]
