#!/usr/bin/env python3
"""Semantic check: replay scene.yaml against the real hash table in hash_trace.py.
Catches what a reference validator cannot: a hand-typed number that is simply wrong."""
import os
import re
import sys

import yaml

import hash_trace as H

here = os.path.dirname(os.path.abspath(__file__))
doc = yaml.safe_load(open(os.path.join(here, "scene.yaml")))
errors, checks = [], 0


def check(ok, msg):
    global checks
    checks += 1
    if not ok:
        errors.append(msg)


for k, v in doc["shared"]["keys"].items():
    check(v["codes"] == H.codes(k), f"shared.keys.{k}.codes {v['codes']} != {H.codes(k)}")
    check(v["sum"] == H.h(k), f"shared.keys.{k}.sum {v['sum']} != {H.h(k)}")

ends = {}
for sc in doc["scenes"]:
    t = next(o["buckets"] for o in sc["objects"] if "buckets" in o)
    m, mode = t["count"], t["mode"]
    where = dict(ends[sc["start"]["from"]]) if "start" in sc else {}   # key -> bucket
    stale = set()
    for n, step in enumerate(sc["steps"]):
        at = f"{sc['scene']} step {n + 1}"
        marks = []
        for op in step["do"]:
            a = op.split()
            if a[0] == "resize":
                m = int(a[2]); stale = set(where)
            elif a[0] == "calc" and len(a) == 4 and a[2] == "index":
                check(int(a[3]) == H.h(a[1]) % m, f"{at}: '{op}' but {H.h(a[1])} mod {m} = {H.h(a[1]) % m}")
            elif a[0] == "calc-rows":
                for pair in a[1:]:
                    k, i = pair.split("=")
                    check(int(i) == H.h(k) % m, f"{at}: '{pair}' but {H.h(k)} mod {m} = {H.h(k) % m}")
            elif a[0] == "put":
                k, i = a[1], int(a[2].split(".")[1])
                taken = {b for kk, b in where.items() if kk != k and kk not in stale}
                want = H.h(k) % m
                if mode == "open":
                    while want in taken:
                        want = (want + 1) % m
                if mode != "list":
                    check(i == want, f"{at}: '{op}' but real code puts {k} at {want}")
                where[k] = i; stale.discard(k)
            elif a[0] in ("miss", "hit"):
                marks.append((a[0], a[1]))
        if marks:   # the compared keys must be a prefix of the real lookup walk for the hit/last key
            target = next((k for kind, k in marks if kind == "hit"), None)
            if target:
                b = H.h(target) % m
                if mode == "list":
                    walk = sorted(where, key=where.get)
                    walk = walk[: walk.index(target) + 1]
                elif mode == "chain":
                    walk = [k for k in where if where[k] == b]          # dict order == put order
                    walk = walk[: walk.index(target) + 1]
                else:
                    walk, i = [], b
                    occ = {v: k for k, v in where.items()}
                    while i in occ:
                        walk.append(occ[i])
                        if occ[i] == target:
                            break
                        i = (i + 1) % m
                check([k for _, k in marks] == walk, f"{at}: compared {[k for _, k in marks]} but real walk is {walk}")
                cm = re.search(r"(\d+) comparisons", step["say"])
                if cm:
                    check(int(cm.group(1)) == len(walk), f"{at}: caption says {cm.group(1)} comparisons, real {len(walk)}")
        for s, mm, r in re.findall(r"(\d+) mod (\d+) is (\d+)", step["say"]):
            check(int(s) % int(mm) == int(r) and int(mm) == m, f"{at}: caption says {s} mod {mm} is {r} (table has {m})")
        lf = re.search(r"[Ll]oad factor (?:of )?(\d+(?:\.\d+)?)", step["say"])
        if lf:
            check(abs(float(lf.group(1)) - len(where) / m) < 1e-9, f"{at}: caption load {lf.group(1)} but real {len(where) / m}")
    ends[sc["scene"]] = where

print(f"{checks} checks, {len(errors)} errors")
for e in errors:
    print("  -", e)
sys.exit(1 if errors else 0)
