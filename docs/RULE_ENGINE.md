# Validation rule engine

Rules are deterministic pure functions returning RuleIssue objects. The registry runs rules in stable name order and keeps structural validation separate from parser diagnostics.
