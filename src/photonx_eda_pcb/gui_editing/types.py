KNOWN_EDIT_TYPES={"rename_net","assign_reference","set_value","set_footprint","merge_nets","split_net","set_component_kind","annotate","set_variant_fit"}
def edit_type_known(kind):return str(kind) in KNOWN_EDIT_TYPES
