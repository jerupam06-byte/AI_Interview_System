from datetime import datetime


def format_datetime(dt) -> str:
    """Formats datetime objects for clean user display."""
    if not dt:
        return "N/A"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except Exception:
            return dt
    return dt.strftime("%b %d, %Y • %I:%M %p")


def get_score_badge_class(score: float) -> str:
    """Returns CSS class for a given numeric score."""
    if score is None:
        return "badge-secondary"
    if score >= 75:
        return "badge-success"
    if score >= 50:
        return "badge-warning"
    return "badge-danger"


def get_score_label(score: float) -> str:
    """Returns qualitative grade label."""
    if score is None:
        return "Unscored"
    if score >= 85:
        return "Placement Ready (Excellent)"
    if score >= 70:
        return "Strong Contender (Good)"
    if score >= 50:
        return "Developing (Average)"
    return "Needs Focused Revision"
