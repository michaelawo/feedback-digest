"""Write the HTML report and the cleaned CSV."""
import csv
from html import escape
from pathlib import Path
from string import Template

TEMPLATES = Path(__file__).parent / "templates"


def bar_rows(rows):
    """Table rows with a bar. rows is a list of (label, count, extra cells)."""
    if not rows:
        return ""
    biggest = max(count for _, count, _ in rows)
    html = []
    for label, count, extra in rows:
        width = round(100 * count / biggest, 1)
        cells = "".join(f'<td class="num">{escape(str(cell))}</td>' for cell in extra)
        html.append(
            f"<tr><th scope='row'>{escape(label)}</th>"
            f"<td class='bar-cell'><span class='bar' style='width:{width}%' "
            f"title='{escape(label)}: {count}'></span>"
            f"<span class='value'>{count}</span></td>{cells}</tr>"
        )
    return "\n".join(html)


def change(now, before):
    if now > before:
        return f"up {now - before}"
    if now < before:
        return f"down {before - now}"
    return "same"


def build_html(summary, source_name, rows_read, skipped, duplicates):
    categories = bar_rows(
        [(c, total, (week, before, change(week, before)))
         for c, total, week, before in summary.by_category]
    )
    routes = bar_rows([(route, total, ()) for route, total in summary.by_route])
    hotspots = "\n".join(
        f"<tr><th scope='row'>{escape(route)}</th><td>{escape(category)}</td>"
        f"<td class='num'>{count}</td><td class='quote'>{escape(example)}</td></tr>"
        for route, category, count, example in summary.hotspots
    ) or "<tr><td colspan='4'>No route has three or more messages of one kind.</td></tr>"
    skipped_list = "\n".join(
        f"<li>line {line}: {escape(reason)}</li>" for line, reason in skipped
    ) or "<li>none</li>"

    period = "no data"
    if summary.total:
        period = f"{summary.first_day:%d %b %Y} to {summary.last_day:%d %b %Y}"

    template = Template((TEMPLATES / "report.html").read_text(encoding="utf-8"))
    return template.substitute(
        css=(TEMPLATES / "report.css").read_text(encoding="utf-8"),
        source=escape(source_name),
        period=period,
        rows_read=rows_read,
        total=summary.total,
        duplicates=duplicates,
        skipped_count=len(skipped),
        categories=categories,
        routes=routes,
        hotspots=hotspots,
        skipped=skipped_list,
    )


def write_csv(items, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["id", "received", "channel", "route", "stop", "category", "duplicate_of", "text"]
        )
        for item in sorted(items, key=lambda item: (item.received, item.id)):
            writer.writerow(
                [item.id, item.received.isoformat(), item.channel, item.route,
                 item.stop, item.category, item.duplicate_of, item.text]
            )
