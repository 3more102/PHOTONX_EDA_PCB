class PhotonXError(Exception):
    """Base exception for PHOTONX."""


class ParseError(PhotonXError):
    """Input data is malformed or inconsistent."""


class UnsupportedFeatureError(ParseError):
    """Input uses syntax that this backend does not support safely."""


class ValidationError(PhotonXError):
    """A reconstructed model failed a required invariant."""
