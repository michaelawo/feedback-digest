from datetime import date

from feedback_digest.models import Feedback


def make(id, text, route="4", day=3, month=11, category="other"):
    return Feedback(
        id=id, received=date(2026, month, day), channel="web", route=route,
        stop="", text=text, category=category,
    )
