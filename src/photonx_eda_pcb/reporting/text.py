from .summary import build_summary
def render_text_report(board)->str:
    s=build_summary(board);c=s["check_counts"];stats=s["stats"]
    return f"PHOTONX report\ntracks={stats['tracks']} pads={stats['pads']} drills={stats['drills']} slots={stats.get('slots',0)} nets={stats['nets']}\ncompleteness={s['completeness']:.3f} quality={s['quality']:.3f}\nchecks: errors={c['error']} warnings={c['warning']} info={c['info']}\n"
