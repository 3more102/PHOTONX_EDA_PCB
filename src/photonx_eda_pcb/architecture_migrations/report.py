def migration_report(plans):return [{"id":p.id,"title":p.title,"status":p.status,"steps":[s.__dict__ for s in p.steps]} for p in plans]
