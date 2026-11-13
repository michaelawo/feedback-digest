"""Count things. Copies are left out of every number here."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import timedelta

HOTSPOT_MINIMUM = 3


@dataclass
class Summary:
    total: int
    first_day: object
    last_day: object
    by_category: list   # (category, total, last 7 days, 7 days before)
    by_route: list      # (route, total)
    hotspots: list      # (route, category, count, example message)


def summarise(items):
    unique = [item for item in items if not item.duplicate_of]
    if not unique:
        return Summary(0, None, None, [], [], [])

    last_day = max(item.received for item in unique)
    week_start = last_day - timedelta(days=6)
    previous_start = week_start - timedelta(days=7)

    totals, this_week, previous_week = Counter(), Counter(), Counter()
    routes = Counter()
    pairs = defaultdict(list)

    for item in unique:
        totals[item.category] += 1
        if item.received >= week_start:
            this_week[item.category] += 1
        elif item.received >= previous_start:
            previous_week[item.category] += 1
        if item.route:
            routes[item.route] += 1
            if item.category != "other":
                pairs[(item.route, item.category)].append(item)

    hotspots = []
    for (route, category), group in pairs.items():
        if len(group) >= HOTSPOT_MINIMUM:
            newest = max(group, key=lambda item: item.received)
            hotspots.append((route, category, len(group), newest.text))
    hotspots.sort(key=lambda h: (-h[2], h[0], h[1]))

    return Summary(
        total=len(unique),
        first_day=min(item.received for item in unique),
        last_day=last_day,
        by_category=[
            (c, n, this_week[c], previous_week[c]) for c, n in totals.most_common()
        ],
        by_route=routes.most_common(10),
        hotspots=hotspots[:10],
    )
