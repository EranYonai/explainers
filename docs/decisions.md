# Design decisions

Why the skill works the way it does. SKILL.md is the contract; this file records the reasons behind it, so
a change can be judged against them. The full design write-up that led here is in the git history
(`docs/design-base-page.md`, removed in the cleanup that added this file).

## Steady controls

Back, Next and Play never move, from the first step to the last, on a phone or a desktop.

- **Measure, then reserve.** When a scene starts, the player draws every step without motion, takes the
  tallest stage and caption, and sets them as `--stage-h` and `--caption-h`. It measures again after fonts
  load and when the width changes. Pages and themes never set a height on `.stage` or `.caption`; the check
  fails if they do.
- **Reader outcomes are measured up front.** A scene lists every outcome a choice can add in `branches`, so
  the reserve already covers them. The earlier idea, growing the stage once after a choice, still moved the
  controls once, so it was dropped.
- **Content that grows goes in a well.** A log or a chat list lives in a fixed-height box that scrolls to its
  newest row (`api.well(el)`), instead of pushing the controls down.
- **Deck sections share one grid cell,** so switching sections changes nothing below the stage.

## A page, not just a scene

An explainer has parts beyond the scene: a hook, a payoff, short prose, sources. They are marked with
`data-slot`, keep one fixed order, and only `intro`, `scene` and `payoff` are required. Writing the parts in
the HTML, with a comment on each, works better than describing them in prose: the agent copies a starter
and deletes what it does not need.

- **One starter per kind** (`concept`, `pr`, `incident`, `onboarding`), each a working page with the right
  parts kept. `concept` has every part and is the default.
- **Shared helpers live in the player.** `.choices` and `.cards` / `.card` were being copied into every page
  under different names, so the player owns them now.

## Numbers come from code

Captions fill `{name}` from `compute(state)`. A missing value renders as `[?name]` and is reported, so the
check fails instead of shipping a wrong number. Random data is seeded (`api.rng`), so captions that quote a
result stay true on every load.

## What the check enforces

`check.mjs` turns the rules a script can see into failures: controls that move, overridden heights, sideways
scroll, missing or misordered page parts, broken citations, a missing theme, literal colors in page styles,
`Math.random`, and `api.branch` without `branches`. What it cannot see (facts, typed numbers in prose,
whether the reader's choice matters) is listed in `references/checks.md` for the agent to check by eye.

## Themes

The gallery (`docs/themes/`) is the pool; the skill ships eight. Six of them are generated from the gallery
by `build.py`, which writes both copies, so they cannot drift. Flight Deck and Transit are hand-written in
the skill folder. Shipped themes leave out the gallery-only tokens (`--sketch`, `--node-rx`).

## Repo checks

`npm run check` builds and checks every example and starter, and CI also fails when a committed example page
differs from a fresh build or the gallery differs from `build.py`'s output. The examples' `index.html` stay
committed because the README and the gallery link to them.
