def stats_report(s):
    return {k:getattr(s,k) for k in s.__dataclass_fields__}
