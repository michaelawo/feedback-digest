import csv

from feedback_digest.__main__ import main
from feedback_digest.analyse import summarise
from feedback_digest.report import build_html
from tests.helpers import make


def test_summary_leaves_out_copies():
    items = [make("A", "Late.", category="delay"), make("B", "Late.", category="delay")]
    items[1].duplicate_of = "A"
    summary = summarise(items)
    assert summary.total == 1
    assert summary.by_category == [("delay", 1, 1, 0)]


def test_summary_of_nothing():
    assert summarise([]).total == 0


def test_week_comparison_uses_the_last_day_in_the_data():
    items = [
        make("A", "Late.", day=8, category="delay"),   # last 7 days: 2 to 8 Nov
        make("B", "Late.", day=2, category="delay"),
        make("C", "Late.", day=1, category="delay"),   # 7 days before
        make("D", "Late.", day=1, month=10, category="delay"),  # older
    ]
    assert summarise(items).by_category == [("delay", 4, 2, 1)]


def test_hotspot_needs_three_messages_on_one_route():
    items = [make(f"A{n}", "Late.", route="4", day=n, category="delay") for n in (1, 2, 3)]
    items += [make(f"B{n}", "Late.", route="6", day=n, category="delay") for n in (1, 2)]
    hotspots = summarise(items).hotspots
    assert [(route, category, count) for route, category, count, _ in hotspots] == [("4", "delay", 3)]


def test_html_escapes_passenger_text():
    items = [make(f"A{n}", "<script>alert(1)</script>", day=n, category="delay") for n in (1, 2, 3)]
    html = build_html(summarise(items), "export.csv", 3, [], 0)
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html


def test_whole_run_on_the_sample_file(tmp_path):
    assert main(["data/sample_feedback.csv", "-o", str(tmp_path)]) == 0
    assert "Feedback digest" in (tmp_path / "report.html").read_text(encoding="utf-8")
    with open(tmp_path / "cleaned.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 122
    assert sum(1 for row in rows if row["duplicate_of"]) == 9


def test_missing_file_gives_exit_code_1(tmp_path, capsys):
    assert main([str(tmp_path / "nope.csv")]) == 1
    assert "Could not read" in capsys.readouterr().err
