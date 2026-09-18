def validate_variant_reconciliation(summary):
    return [] if isinstance(summary.get("ready"),bool) else ["VARIANT_RECONCILIATION_BAD_READY"]
