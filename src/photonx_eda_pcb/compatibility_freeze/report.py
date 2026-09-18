def compatibility_freeze_report(d):return {"passed":d.passed,"blockers":list(d.blockers),"warnings":list(d.warnings),"feature_count":d.feature_count,"migration_count":d.migration_count}
