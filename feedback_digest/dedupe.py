"""Find messages that were sent more than once.

People often send the same complaint through the web form and by email, or
press submit twice. Counting those as separate complaints makes a problem look
bigger than it is, so copies are marked and left out of the statistics.

Two messages count as copies when they are about the same route, arrived
within a few days of each other and use almost the same words. The same
complaint from different people weeks apart is NOT a copy. That is a recurring
problem and is exactly what the report should show.
"""
import re
from collections import defaultdict

STOPWORDS = {
    "the", "and", "was", "were", "for", "that", "this", "with", "have", "has",
    "had", "not", "but", "you", "your", "are", "from", "there", "very", "again",
    "please", "thanks", "thank",
}


def word_set(text):
    words = re.findall(r"\w+", text.lower())
    # short words say little, but numbers do: "20 minutes" is not "45 minutes"
    return {w for w in words if (len(w) > 2 or w.isdigit()) and w not in STOPWORDS}


def similarity(a, b):
    """Jaccard similarity: shared words divided by all words, from 0 to 1."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class Groups:
    """Union-find. Puts items into groups and finds which group an item is in."""

    def __init__(self, size):
        self.parent = list(range(size))

    def find(self, i):
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]  # shorten the path
            i = self.parent[i]
        return i

    def join(self, i, j):
        root_i, root_j = self.find(i), self.find(j)
        # keep the smaller index as root, so the root is the earliest message
        if root_i < root_j:
            self.parent[root_j] = root_i
        else:
            self.parent[root_i] = root_j


def mark_duplicates(items, threshold=0.75, max_days=3):
    """Set duplicate_of on every copy and return how many copies were found."""
    by_route = defaultdict(list)
    for item in items:
        by_route[item.route].append(item)

    found = 0
    for group in by_route.values():
        # Sorted by date, so the inner loop can stop as soon as the gap is
        # too big. This avoids comparing every message with every other one.
        group.sort(key=lambda item: (item.received, item.id))
        words = [word_set(item.text) for item in group]
        groups = Groups(len(group))

        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                if (group[j].received - group[i].received).days > max_days:
                    break
                if similarity(words[i], words[j]) >= threshold:
                    groups.join(i, j)

        for i, item in enumerate(group):
            root = groups.find(i)
            if root != i:
                item.duplicate_of = group[root].id
                found += 1
    return found
