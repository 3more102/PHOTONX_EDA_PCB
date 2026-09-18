def numeric_series(history,field):
    return [(label,getattr(stats,field)) for label,stats in history.all()]
