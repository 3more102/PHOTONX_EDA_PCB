from .summary import diff_summary

def diff_report(diff):
    s=diff_summary(diff)
    return f"diff total={s['total']} added={s['added']} removed={s['removed']} changed={s['changed']}"
