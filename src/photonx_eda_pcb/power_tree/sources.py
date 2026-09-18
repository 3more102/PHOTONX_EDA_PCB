SOURCE_KINDS=("regulator","ldo","dc-dc","buck","boost","battery","connector")
def is_power_source_kind(kind):return any(x in str(kind).lower() for x in SOURCE_KINDS)
