from .summary import build_summary
def render_text_report(board)->str:
    s=build_summary(board); c=s["check_counts"]
    return f"PHOTONX report\ntracks={s['stats']['tracks']} pads={s['stats']['pads']} nets={s['stats']['nets']}\ncompleteness={s['completeness']:.3f} quality={s['quality']:.3f}\nchecks: errors={c['error']} warnings={c['warning']} info={c['info']}\n"
