def run_invalidation_matrix(stages,expectations):
    from .audit import audit_invalidation
    return [audit_invalidation(stages,x) for x in expectations]
