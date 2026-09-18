# Structured KiCad Schematic Export
The structured exporter writes a deterministic KiCad 6+ style s-expression subset with header, root UUID, embedded symbol stubs, symbol instances, wires, local/global labels and root sheet instance metadata.

The output is structurally parsed by PHOTONX. Native KiCad validation is not claimed unless kicad-cli is actually run successfully.
