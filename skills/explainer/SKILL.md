---
name: explainer
description: Make an interactive, silent, mobile-first HTML explainer of a topic, a pull request, an incident or an onboarding subject, with step-through scenes, captions that carry the teaching, and something the reader controls. Use when asked to "explain X visually", "make an explainer", or walk someone through how something works.
---

# Explainer

Turn a topic into one self-contained HTML page: short prose, a scene the reader steps through
(Back / Next / Play), captions that do the teaching, and one thing the reader controls. Silent by design:
no voice, no video. Built from a shared player, so you write only content and a little drawing code.

Paths below are relative to this skill's folder (`<skill>`).

## 1. Brief (one message, or none)

If the request already says who it is for and what should click (a PR, an incident, a precise topic),
skip the questions and state your brief in one line. Otherwise ask at most four, in one message:
1. Who reads it, and what do they already know?
2. What one idea should click by the end?
3. Which wrong idea should break?
4. What can be left out?

For a PR or incident, read the diff or the timeline first and draw the brief from it.
Never put confidential details (internal names, hosts, customers) on the page; teach the pattern.

## 2. Story in four beats

Write these down before any code (see `references/story-beats.md`):
- **Hook:** one question in big type that the reader cannot answer yet.
- **Setup:** one or two frames of what the reader already knows.
- **Mechanism:** 5 to 15 steps. Each step states what is true now, not how it moves.
- **Payoff:** one sentence, stamped large, that answers the hook.

Pick the **reader action**: choose an input, approve a step, pick a route, drag a value. It should change
what happens next, with real logic behind it.

## 3. Build

1. Copy `templates/page.src.html` to the output folder as `<slug>.src.html`.
2. Pick a theme by topic (change the `explainer:theme/<name>` link):

   | Theme | Fits |
   |---|---|
   | `inkwell` (default) | step-by-step reasoning, debugging, anything sketched by hand |
   | `flight-deck` | systems and tools, agents, pipelines, modes and switches |
   | `transit` | flows and architectures, request paths, state machines, routes |
   | `gruvbox`, `kanagawa`, `one-half`, `dracula`, `rose-pine` | editor palettes: same layout, the reader's favorite colors |

3. Write the content with the player (`templates/player.js` documents the API at the top;
   `references/scene-patterns.md` has the patterns). Rules:
   - **States, not animations.** Steps use `set` (carries forward) and `mark` (this step only);
     `draw(state)` makes the page match. CSS transitions do the motion.
   - **Numbers come from code.** Any number in a caption is `{name}` filled by `compute(state)`,
     or produced by a function that runs the real logic (a search, a count, a simulation). Never type a result.
   - **Random is seeded:** `api.rng(seed)`. Same seed, same page.
   - **Theme tokens only:** `var(--ink)`, `var(--accent)`, ... Never hard-code a color.
   - **Phone first:** 390 px wide with no sideways scroll; text in SVG at least 12 px on a phone.
   - **Captions:** one or two sentences, under 200 characters, plain words.
   - **Current tech:** for tools, libraries and services, check facts against primary sources and list them
     in a Sources section. Timeless topics (algorithms, concepts) need none.
4. Build: `node <skill>/scripts/build.mjs <slug>.src.html -o <slug>.html` writes one self-contained file.

The player owns these class names, so do not reuse them for your own elements: `scene`, `stage`, `caption`,
`stepno`, `controls`, `prev`, `next`, `play`, `playgroup`, `speed-now`, `speed-menu`, `speed-opts`, `dots`,
`sec`, `deck`, `on`, `done`. Layout helpers you may use: `col` (reading column), `wide` (scene width),
`stack` (vertical gap), `hook`, `payoff`, `note`, `choices` and `pick` (rows of reader buttons).

## 4. Check once, fix once

Run `node <skill>/scripts/check.mjs <slug>.html` (add `--sheet <path.png>` to choose where the contact sheet goes). It walks every step at phone and desktop width and
prints PASS or FAIL with a short list (JS errors, missing caption values, sideways scroll, content wider
than its scene), plus a contact sheet image of every step. Look at the contact sheet. Fix with targeted
edits, rebuild, re-run once. See `references/checks.md` for what it cannot catch and you must eyeball.
If it prints SKIP, Playwright is not installed; say so and open the page yourself if you can.

## 5. Hand over

Give the path to `<slug>.html` and one line on what the reader does on the page.
