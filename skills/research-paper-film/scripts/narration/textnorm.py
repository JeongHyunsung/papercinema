"""Shared helpers: printed -> spoken normalization and word error counts."""
import re
import numpy as np


def spoken(text, table):
    """Apply a print->spoken table [(printed, spoken), ...] to text."""
    t = text
    for a, b in sorted(table, key=lambda x: -len(x[0])):
        t = re.sub(r"(?<![\w.,-])" + re.escape(a) + r"(?![\w-])", b, t)
    return t


def words(text):
    return re.sub(r"[^a-z0-9' ]", " ", text.lower().replace("-", " ")).split()


def n_spoken(text, table):
    return len(re.findall(r"[A-Za-z0-9'\-]+", spoken(text, table)))


def edits(ref, hyp):
    """Levenshtein distance between word lists."""
    d = np.arange(len(hyp) + 1)
    for i, x in enumerate(ref, 1):
        p = d.copy(); d[0] = i
        for j, y in enumerate(hyp, 1):
            d[j] = min(p[j] + 1, d[j - 1] + 1, p[j - 1] + (x != y))
    return int(d[-1])
