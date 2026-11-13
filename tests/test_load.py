from datetime import date

import pytest

from feedback_digest.load import clean_route, load_feedback, parse_date

HEADER = "id,received,channel,route,stop,text\n"


def write(tmp_path, body, header=HEADER):
    path = tmp_path / "feedback.csv"
    path.write_text(header + body, encoding="utf-8")
    return path


def test_parse_date_accepts_three_formats():
    expected = date(2026, 11, 3)
    assert parse_date("2026-11-03") == expected
    assert parse_date("2026.11.03.") == expected
    assert parse_date("03/11/2026") == expected
    assert parse_date("last tuesday") is None


@pytest.mark.parametrize(
    "raw, expected",
    [("4", "4"), ("Tram 4 ", "4"), ("bus 7", "7"), ("m3", "M3"), ("metro 3", "M3"), ("100e", "100E"), ("", "")],
)
def test_clean_route(raw, expected):
    assert clean_route(raw) == expected


def test_loads_and_cleans_a_row(tmp_path):
    path = write(tmp_path, 'F1,2026.11.03.,Web,tram 6,Blaha Lujza tér,"  Late   again. "\n')
    items, skipped = load_feedback(path)
    assert skipped == []
    item = items[0]
    assert (item.route, item.channel, item.text) == ("6", "web", "Late again.")
    assert item.received == date(2026, 11, 3)
    assert item.stop == "Blaha Lujza tér"


def test_bad_rows_are_skipped_with_a_reason(tmp_path):
    path = write(
        tmp_path,
        "F1,2026-11-03,web,4,,Late.\n"
        "F2,2026-11-03,web,4,,\n"
        "F3,someday,web,4,,Late.\n"
        "F1,2026-11-04,web,4,,Dirty.\n",
    )
    items, skipped = load_feedback(path)
    assert [item.id for item in items] == ["F1"]
    assert [line for line, _ in skipped] == [3, 4, 5]
    assert "empty text" in skipped[0][1]
    assert "date" in skipped[1][1]
    assert "id" in skipped[2][1]


def test_missing_column_is_an_error(tmp_path):
    path = write(tmp_path, "F1,2026-11-03,Late.\n", header="id,received,text\n")
    with pytest.raises(ValueError, match="route"):
        load_feedback(path)


def test_file_saved_from_excel_with_bom(tmp_path):
    path = tmp_path / "feedback.csv"
    path.write_text(HEADER + "F1,2026-11-03,web,4,,Late.\n", encoding="utf-8-sig")
    items, _ = load_feedback(path)
    assert len(items) == 1
