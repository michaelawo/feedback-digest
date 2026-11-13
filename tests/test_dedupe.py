from feedback_digest.dedupe import Groups, mark_duplicates, similarity, word_set
from tests.helpers import make

LATE = "The tram was 20 minutes late at Corvin-negyed this morning."


def test_similarity():
    assert similarity({"a", "b"}, {"a", "b"}) == 1
    assert similarity({"a", "b"}, {"c"}) == 0
    assert similarity({"a", "b", "c"}, {"a", "b", "d"}) == 0.5
    assert similarity(set(), set()) == 0


def test_word_set_ignores_case_punctuation_and_filler():
    assert word_set("The tram WAS late!") == {"tram", "late"}


def test_word_set_keeps_numbers():
    assert "20" in word_set("20 minutes late")


def test_groups():
    groups = Groups(5)
    groups.join(3, 4)
    groups.join(1, 3)
    assert groups.find(4) == 1
    assert groups.find(0) == 0
    assert groups.find(2) == 2


def test_resent_message_is_a_copy_of_the_first():
    items = [make("A", LATE, day=3), make("B", LATE + " Please fix this.", day=4)]
    assert mark_duplicates(items) == 1
    assert items[1].duplicate_of == "A"
    assert items[0].duplicate_of == ""


def test_three_copies_point_to_the_earliest():
    items = [make("C", LATE, day=5), make("A", LATE, day=3), make("B", LATE, day=4)]
    assert mark_duplicates(items) == 2
    by_id = {item.id: item.duplicate_of for item in items}
    assert by_id == {"A": "", "B": "A", "C": "A"}


def test_same_words_weeks_apart_is_a_recurring_problem_not_a_copy():
    items = [make("A", LATE, day=3, month=10), make("B", LATE, day=3, month=11)]
    assert mark_duplicates(items) == 0


def test_same_words_on_another_route_is_not_a_copy():
    items = [make("A", LATE, route="4"), make("B", LATE, route="6")]
    assert mark_duplicates(items) == 0


def test_different_delay_is_not_a_copy():
    items = [make("A", "Tram was 20 minutes late."), make("B", "Tram was 45 minutes late.")]
    assert mark_duplicates(items) == 0


def test_different_messages_are_not_copies():
    items = [make("A", LATE), make("B", "The seats were dirty and it smelled.")]
    assert mark_duplicates(items) == 0
