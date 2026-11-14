#!/usr/bin/env python3
"""Reference hash table for the explainer. This is the "real code" a trace layer would run.

  python3 hash_trace.py search   -> candidate key sets (names only) that tell the story
  python3 hash_trace.py trace    -> JSON trace of every insert / lookup / rehash / probe event
"""
import itertools
import json
import sys

KEYS = ["cat", "fox", "bee", "ant", "act", "cow"]          # insertion order, chaining scenes
PROBE_ORDER = ["fox", "bee", "ant", "cat", "act", "cow"]    # insertion order, open addressing scene


def codes(key):
    return [ord(ch) for ch in key]


def h(key):
    return sum(codes(key))


def calc(key, m):
    return {"key": key, "codes": codes(key), "sum": h(key), "mod": m, "index": h(key) % m}


class Chained:
    def __init__(self, m):
        self.m = m
        self.buckets = [[] for _ in range(m)]
        self.n = 0

    def insert(self, key):
        i = h(key) % self.m
        collided = bool(self.buckets[i])
        self.buckets[i].append(key)
        self.n += 1
        return {"op": "insert", **calc(key, self.m), "collision": collided,
                "chain": list(self.buckets[i]), "n": self.n, "load": self.n / self.m}

    def lookup(self, key):
        i = h(key) % self.m
        walked = []
        for k in self.buckets[i]:
            walked.append(k)
            if k == key:
                return {"op": "lookup", **calc(key, self.m), "walked": walked, "found": True}
        return {"op": "lookup", **calc(key, self.m), "walked": walked, "found": False}

    def resize(self, m2):
        old = self.buckets
        self.m, self.buckets = m2, [[] for _ in range(m2)]
        moves = []
        for i, chain in enumerate(old):
            for k in chain:
                j = h(k) % m2
                self.buckets[j].append(k)
                moves.append({**calc(k, m2), "from": i, "to": j})
        return {"op": "resize", "m": m2, "moves": moves, "buckets": self.buckets,
                "n": self.n, "load": self.n / m2}


class Probed:
    def __init__(self, m):
        self.m = m
        self.slots = [None] * m

    def insert(self, key):
        i = h(key) % self.m
        probes = []
        while self.slots[i] is not None:
            probes.append({"slot": i, "holds": self.slots[i]})
            i = (i + 1) % self.m
        self.slots[i] = key
        return {"op": "probe-insert", **calc(key, self.m), "probes": probes, "placed": i}

    def lookup(self, key):
        i = h(key) % self.m
        probes = []
        while self.slots[i] is not None:
            probes.append({"slot": i, "holds": self.slots[i]})
            if self.slots[i] == key:
                return {"op": "probe-lookup", **calc(key, self.m), "probes": probes, "found": True}
            i = (i + 1) % self.m
        return {"op": "probe-lookup", **calc(key, self.m), "probes": probes, "found": False}


def trace():
    out = {"hash": [calc(KEYS[0], 4)]}
    t = Chained(4)
    out["chain"] = [t.insert(k) for k in KEYS]
    out["chain"].append(t.lookup(KEYS[4]))
    out["buckets4"] = [list(b) for b in t.buckets]
    out["resize"] = t.resize(8)
    p = Probed(8)
    out["probe"] = [p.insert(k) for k in PROBE_ORDER]
    out["probe"].append(p.lookup(PROBE_ORDER[-1]))
    out["slots"] = p.slots
    return out


WORDS = """cat act dog pan nap owl low bat tab bee ant fox cow pig hen yak elk emu eel rat art tar
arm ram car arc tea eat pot top net ten pin nip tip pit bus sub gum mug pal lap saw was now own
ape pea jay kiwi fig yam oak elm ash ivy fir bay sky sun map key log job box bug row col""".split()


def search():
    """Print key sets (names only) that satisfy the storyboard. See NOTES.md for why names only."""
    anagrams = [(a, b) for a, b in itertools.permutations(WORDS, 2) if sorted(a) == sorted(b)]
    seen = 0
    for k1, k5 in anagrams:
        b, h8 = h(k1) % 4, h(k1) % 8
        if h8 + 2 > 7:
            continue
        rest = [w for w in WORDS if sorted(w) != sorted(k1) and len(w) == 3]
        for k3 in rest:                                   # first collision: same bucket of 4, leaves on resize
            if h(k3) % 4 != b or h(k3) % 8 == h8:
                continue
            for k2, k4, k6 in itertools.permutations([w for w in rest if w != k3 and h(w) % 4 != b], 3):
                keys = [k1, k2, k3, k4, k5, k6]
                if h(k2) % 4 == h(k4) % 4 or h(k6) % 4 != h(k2) % 4:
                    continue                              # buckets of 4 end up 3 / 2 / 1 / 0
                homes = [h(k) % 8 for k in keys]
                if len(set(homes)) != 5:                  # only the anagram pair still collides at 8
                    continue
                if (h8 + 1) not in homes or (h8 + 2) in homes:
                    continue                              # a neighbour gets displaced, next slot is free
                if (homes[homes.index(h8 + 1)] == h(k3) % 8):
                    continue
                print(" ".join(keys))
                seen += 1
                if seen >= 400:
                    return


if __name__ == "__main__":
    if sys.argv[1:] == ["search"]:
        search()
    else:
        json.dump(trace(), sys.stdout, indent=1)
        print()
