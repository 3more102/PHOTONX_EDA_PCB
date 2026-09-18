from .model import MigrationPlan,MigrationStep
def default_migrations():
    return [
        MigrationPlan("MIG-VALIDATION","Normalize validation outputs",(
            MigrationStep("legacy-validation","photonx_eda_pcb.validation.ValidationIssue","photonx_eda_pcb.validation_bridge.UnifiedIssue","adapter"),
            MigrationStep("checks","photonx_eda_pcb.checks.CheckIssue","photonx_eda_pcb.validation_bridge.UnifiedIssue","adapter"),
            MigrationStep("rules","photonx_eda_pcb.validation_rules.RuleIssue","photonx_eda_pcb.validation_bridge.UnifiedIssue","adapter"),
        ),"active"),
        MigrationPlan("MIG-REPORTING","Compose reporting surfaces",(
            MigrationStep("legacy-reporting","photonx_eda_pcb.reporting.py summary","photonx_eda_pcb.reporting_bridge.UnifiedReport","compatibility_facade"),
            MigrationStep("package-reporting","photonx_eda_pcb.reporting package","photonx_eda_pcb.reporting_bridge.UnifiedReport","composition"),
        ),"active"),
    ]
