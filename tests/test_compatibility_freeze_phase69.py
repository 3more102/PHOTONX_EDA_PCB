from photonx_eda_pcb.compatibility_matrix.model import CompatibilityMatrix,CompatibilityEntry
from photonx_eda_pcb.architecture_migrations.model import MigrationPlan,MigrationStep
from photonx_eda_pcb.compatibility_freeze import evaluate_compatibility_freeze
def test_compatibility_freeze_blocks_unsupported_and_breaking():
    m=CompatibilityMatrix([CompatibilityEntry("arc","gerber","unsupported","",())])
    mig=[MigrationPlan("M","breaking",(MigrationStep("s","a","b","replace",True),),"active")]
    d=evaluate_compatibility_freeze(m,mig)
    assert not d.passed and any("UNSUPPORTED" in x for x in d.blockers) and any("BREAKING_MIGRATION" in x for x in d.blockers)
