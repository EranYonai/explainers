# Field report: hash tables and collisions

Five scenes (list scan, hash, chaining + lookup, resize, linear probing). `index.html` is built from
`scene.yaml` by `build.py`; a ~150-line runtime in the page folds the `do` lists into state.

## Did the states layer cover it?
Yes for the drawing, no for the truth. All five scenes are states only: no `trace:`, no `component:`.
But every interesting value on screen (codes, sums, `mod` results, bucket indexes, probe targets,
comparison counts) is the output of an algorithm, restated by hand.

What I actually did:
- I could not even pick the keys without code. `hash_trace.py search` found a key set that tells the
  story (first collision, anagram pair, clean split at 8, one displaced neighbour when probing).
- I then typed all numbers by hand from mental arithmetic. `verify.py` replays the YAML against a real
  table: 66 checks, 0 errors. So hand-written states were correct here, but only provably so because
  a script checked them. I have not mutation-tested the verifier.

Verdict on traces: a trace would be the better source of truth for facts, a worse one for telling.
A trace gives one event per key; the story wants "old bucket 0: two stay, one moves" as one step with a
written caption. Best fit: **states authored by hand, checked by a trace** (`check: hash_trace.py`),
or `{sum(cat) mod table.count}` expressions in `say`/`do`. Sorting needs generation; this needs assertion.

## Primitives used / wished for
Used (all NEW): vertical `buckets` (modes chain, open, list), key `items`, a `calc` worksheet, load
readout derived from the table, `start: {from: scene}`, `resize` with stale items.
Wished: persistent facts vs per-step marks as a first-class distinction (I restate `miss cat` each
step); an `insert`/`lookup` verb on a smart table primitive; named beats.

## What YAML could not express (done by hand in JS/HTML)
Worksheet layout, the pill entering from the inbox, chain ordering during a rehash (fresh before stale),
desktop two-column layout, the hook and payoff typography, all prose.

## Compiler: saved / got in the way
Saved: controls, fold-to-state, Back for free, layout, load meter. In the way: `calc` is too specific
to be a primitive; it is really a small component. Multi-key steps needed a second mode (`calc-rows`).

## What an AI author would get wrong
Arithmetic and mod results in captions; forgetting that resize changes every index; probe order
depending on insertion order; captions that drift from `do`. A reference validator catches none of these.

## 9:16 silent reel (60-90s)
35 steps is too many: needs `reel: {include: [...]}` to pick ~14 steps, per-step `hold` durations
(or derived from caption word count), captions as the top third in big type, word- or phrase-timed
reveal (`say` split with `|`), and `hook`/`payoff` as full-screen cards. The 360-wide stage already
fits portrait.

## Verdict
The states layer is enough to draw a data-structure explainer, but it needs a semantic check against
real code to be trusted; add "trace as validator" to the plan.

Draft status: checked at 390px and 1100px (no sideways scroll, no JS errors); only two frames eyeballed.
