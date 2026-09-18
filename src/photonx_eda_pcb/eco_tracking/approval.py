from dataclasses import replace
def approve_change(change):return replace(change,approved=True)
def reject_change(change):return replace(change,approved=False)
def all_approved(eco):return all(x.approved for x in eco.changes)
