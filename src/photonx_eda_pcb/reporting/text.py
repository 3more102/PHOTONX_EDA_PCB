from .summary import build_summary


def render_text_report(board) -> str:
    summary = build_summary(board)
    counts = summary["check_counts"]
    stats = summary["stats"]
    return (
        "PHOTONX report\n"
        f"tracks={stats['tracks']} pads={stats['pads']} drills={stats['drills']} "
        f"slots={stats.get('slots', 0)} routes={stats.get('routes', 0)} "
        f"regions={stats.get('regions', 0)} nets={stats['nets']}\n"
        f"completeness={summary['completeness']:.3f} "
        f"quality={summary['quality']:.3f}\n"
        f"checks: errors={counts['error']} warnings={counts['warning']} "
        f"info={counts['info']}\n"
    )
