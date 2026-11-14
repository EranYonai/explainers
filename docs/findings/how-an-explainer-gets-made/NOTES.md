# Field notes: "How an explainer gets made" (meta + git bisect)

Five scenes and one slider component, hand-written. `scene.yaml` is what I would have wanted to write.

## What fit where
- **States:** scenes 1 to 4. Each is one pure draw(state) per step.
- **Traces:** the final bisect. The reader picks the culprit, so a 12-line binary search emits steps and captions. It caught a plan error: the plan's demo says "up to 7" one-by-one tests; with c8 known bad it is 6.
- **Components:** the cost slider (2^k commits, k tests).

## Primitives
Used: commits, pointer, range. Missed: chat, card with fillable rows, named slots, rough sketch import, margin note, terminal log, diff, `source` (code view bound to a scene), `embed`/`frame` (scene inside a scene), reader `choice` feeding a trace.

## What YAML could not express
- Scenes that reference other scenes: showing a scene's source, and a frozen, deliberately broken frame of it.
- Computed values in text. The overlap percentage is measured live with getBBox.
- Conditional captions inside a trace ("c8 was never tested"). Per-event templates are too flat.
- `do: [verb target "text"]` is invalid YAML. Text-carrying actions had to become one-key maps.

## Compiler: saved vs in the way
Saved: the player (controls, dots, keys, aria-live), three copies of the bisect view, and layout stability, which took most of my CSS time. In the way: scenes 1 and 2 are HTML layouts with wrapping text. An SVG-first compiler would fight them.

## What an AI author gets wrong here
Off-by-one test counts; labels clipped at c2/c8 on phones; captions describing motion instead of facts; a forgotten `hide`; height jumps between steps; reconstructed dialogue passed off as a transcript. Checks worth building: label overlap, label outside viewBox, per-step height diff, caption numbers must come from the trace.

## Export to a silent 9:16 reel (60 to 90 s)
Export scene 5 between `hook` and `payoff` cards: about 11 beats. The stage becomes a band in 1080x1920 and the caption is the largest element. YAML needs `hold:` per step (default from word count), optional word-timed `say`, a fixed `choice` value, a `reel: { include: [...] }` list, and a safe area for platform UI.

## Verdict
States and traces hold up, but the flagship is mostly HTML-shaped scenes and scene-to-scene references, so the engine needs HTML primitives and `embed` before it can build its own launch page.
