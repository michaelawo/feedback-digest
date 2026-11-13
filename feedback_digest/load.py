"""Read the feedback export and clean it up."""
import csv
from datetime import datetime

from feedback_digest.models import Feedback

REQUIRED_COLUMNS = ("id", "received", "route", "stop", "text")

# The export mixes these, depending on who typed the row in.
DATE_FORMATS = ("%Y-%m-%d", "%Y.%m.%d.", "%d/%m/%Y")


def parse_date(value):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            pass
    return None


def clean_route(value):
    """'Tram 4' -> '4', 'metro 3' -> 'M3', ' 100e ' -> '100E'."""
    value = value.strip().upper()
    is_metro = value.startswith("METRO")
    for word in ("TRAM", "BUS", "METRO", "LINE"):
        value = value.replace(word, "")
    value = value.replace(" ", "")
    if is_metro and value and not value.startswith("M"):
        value = "M" + value
    return value


def load_feedback(path):
    """Return (items, skipped). skipped is a list of (line number, reason)."""
    items = []
    skipped = []
    seen_ids = set()

    # utf-8-sig also handles files saved from Excel, which start with a BOM
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing column(s): {', '.join(missing)}")

        for row in reader:
            line = reader.line_num
            item_id = (row["id"] or "").strip()
            text = " ".join((row["text"] or "").split())
            received = parse_date(row["received"] or "")

            if not text:
                skipped.append((line, "empty text"))
            elif received is None:
                skipped.append((line, f"unreadable date '{row['received']}'"))
            elif not item_id or item_id in seen_ids:
                skipped.append((line, f"missing or repeated id '{item_id}'"))
            else:
                seen_ids.add(item_id)
                items.append(
                    Feedback(
                        id=item_id,
                        received=received,
                        channel=(row.get("channel") or "").strip().lower(),
                        route=clean_route(row["route"] or ""),
                        stop=(row["stop"] or "").strip(),
                        text=text,
                    )
                )
    return items, skipped
