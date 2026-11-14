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
what happens next, with real logic behind it, and it is about the topic: the reader plays with the thing
being explained, never with how the page was made.

Rules that keep it readable for someone who knows nothing yet:
- **One topic per page.** If you need a second subject to illustrate the first, you have two pages.
- **Show first, explain after.** The first scene step is a picture, not text. Every step changes
  something the reader can see; a step that only changes the caption is a paragraph, so cut it.
- **No undefined words.** Use the reader's words. A term the reader needs gets one plain sentence the
  first time it appears; jargon from this skill (beat, frame, state, brief) never reaches the page.
- **Little code on screen.** A short line at most, and only when the code is the topic.

## 3. Build

1. Copy a starter to the output folder as `<slug>.src.html`. Each is a working page with the right parts
   already kept; replace the placeholders, keep the parts you need, delete the rest, never reorder them.

   | Starter (`templates/kinds/`) | For |
   |---|---|
   | `concept.src.html` | how something works (the default) |
   | `pr.src.html` | a pull request: summary for reviewers, the old and new path side by side |
   | `incident.src.html` | an incident review: timeline, the path the failure took, where to stop it |
   | `onboarding.src.html` | a newcomer's first look at a system, with a glossary and a link to the next part |

   `templates/page.src.html` has every part with a comment saying what goes there, for anything else.
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
   - **Steady controls:** the player reserves the tallest step's height, so never set a height on `.stage`
     or `.caption`. Lists that grow go in `api.well(el)`. Reader choices list their outcomes in `branches`.
   - **Captions:** one or two sentences, under 200 characters, plain words.
   - **Current tech:** for tools, libraries and services, check facts against primary sources, list them in
     the Sources part (`<li id="src-1">` with a link and a version or date) and cite them in prose with
     `<a class="cite" href="#src-1">[1]</a>`. Timeless topics (algorithms, concepts) need none.
4. Build: `node <skill>/scripts/build.mjs <slug>.src.html -o <slug>.html` writes one self-contained file.

The player owns these class names, so do not reuse them for your own elements: `scene`, `stage`, `caption`,
`stepno`, `controls`, `prev`, `next`, `play`, `playgroup`, `speed-now`, `speed-menu`, `speed-opts`, `dots`,
`dock`, `well`, `measuring`, `sec`, `deck`, `on`, `done`. Page parts (use them only for their part):
`masthead`, `kind`, `dek`, `meta`, `tldr`, `prose`, `glossary`, `sources`, `cite`. Layout helpers you may use:
`col` (reading column), `wide` (scene width), `stack` (vertical gap), `hook`, `payoff`, `note`, `choices`
and `pick` (rows of reader buttons).

## 4. Check once, fix once

Run `node <skill>/scripts/check.mjs <slug>.html` (add `--sheet <path.png>` to choose where the contact sheet goes). It walks every step at phone and desktop width and
prints PASS or FAIL with a short list (JS errors, missing caption values, controls that move, sideways
scroll, content wider than its scene, missing page parts, broken citations), plus a contact sheet image of
every step. It clicks `.choices button` to play the reader; if your reader buttons use other classes, add
`--click "<selector>"`. Look at the contact sheet. Fix with targeted
edits, rebuild, re-run once. See `references/checks.md` for what it cannot catch and you must eyeball.
If it prints SKIP, Playwright is not installed; say so and open the page yourself if you can.

Then do a **cold read**: read only the hook, the captions in order and the payoff, as someone who has never
heard of the topic. Can you say in one sentence what you learned? Does any caption lean on a word that was
never explained, or on a picture you cannot see yet? If yes, fix that step. If you can start a fresh agent,
give it only that text and ask the same question.

## 5. Hand over

Give the path to `<slug>.html` and one line on what the reader does on the page.
