"""Command line: python -m feedback_digest data/sample_feedback.csv"""
import argparse
import sys
from pathlib import Path

from feedback_digest.analyse import summarise
from feedback_digest.classify import classify_all
from feedback_digest.dedupe import mark_duplicates
from feedback_digest.load import load_feedback
from feedback_digest.report import build_html, write_csv


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="feedback_digest",
        description="Turn a passenger feedback export into a summary report.",
    )
    parser.add_argument("csv_file", help="the feedback export")
    parser.add_argument("-o", "--out", default="output", help="folder for the results (default: output)")
    args = parser.parse_args(argv)

    try:
        items, skipped = load_feedback(args.csv_file)
    except (OSError, ValueError) as error:
        print(f"Could not read {args.csv_file}: {error}", file=sys.stderr)
        return 1

    duplicates = mark_duplicates(items)
    classify_all(items)
    summary = summarise(items)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    html = build_html(summary, Path(args.csv_file).name, len(items) + len(skipped), skipped, duplicates)
    (out / "report.html").write_text(html, encoding="utf-8")
    write_csv(items, out / "cleaned.csv")

    print(f"{len(items) + len(skipped)} rows read, {len(skipped)} skipped, {duplicates} copies left out")
    print(f"{summary.total} messages counted")
    print(f"Report: {out / 'report.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
