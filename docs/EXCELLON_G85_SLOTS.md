# Excellon G85 Canned Slots

PHOTONX supports a narrow G85 canned-slot subset with explicit start and end coordinates and an already-selected drill tool.

Accepted representations include the conventional form:

`X...Y...G85X...Y...`

and the historic helper-compatible form:

`G85X...Y...X...Y...`

The selected drill tool diameter becomes the reconstructed slot width. Plating remains unknown unless independent evidence establishes it.

General routed drill geometry (G00/G01/G02/G03) is still rejected in strict mode.
