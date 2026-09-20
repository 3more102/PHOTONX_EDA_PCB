import uuid


_PHOTONX_UUID_PREFIX = "https://photonx.local/"


def photonx_uuid(name):
    """Return the stable UUID used for PhotonX-generated KiCad objects."""
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            _PHOTONX_UUID_PREFIX + str(name),
        )
    )
