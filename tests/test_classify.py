import pytest

from feedback_digest.classify import classify


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Tram was 20 minutes late again.", "delay"),
        ("So crowded I could not get on.", "crowding"),
        ("Dirty seats and litter everywhere.", "cleanliness"),
        ("The inspector was rude.", "staff"),
        ("Machine took my money, no ticket.", "ticketing"),
        ("The lift is broken, I use a wheelchair.", "accessibility"),
        ("The display showed the wrong times.", "information"),
        ("Platform was slippery and dangerous.", "safety"),
        ("I left my umbrella on board.", "other"),
        ("", "other"),
    ],
)
def test_classify(text, expected):
    assert classify(text) == expected


def test_passenger_is_not_a_ticketing_word():
    # "pass" is a keyword, "passenger" must not match it
    assert classify("A passenger asked me the way.") == "other"


def test_most_matching_words_wins():
    text = "The driver was fine, but the tram was late and I waited 20 minutes."
    assert classify(text) == "delay"
