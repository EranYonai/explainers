# Design: a resilient, extensible base page

Status: proposal, not built. Scope: the shared player (`player.js`, `player.css`), the page template,
the themes, `SKILL.md` and `check.mjs`.

Two goals:

1. **Nothing the reader taps ever moves.** Back, Next and Play stay put from the first step to the last,
   on a phone and on a desktop, whatever a scene draws.
2. **An explainer is a page, not just a scene.** Headline, hook, the scene, a payoff, short prose and
   sources, with optional parts so the same base fits a concept, a PR, an incident or onboarding.

---

## 1. Layout stability

### What goes wrong today (measured)

I walked every step of every example with Playwright and recorded where the Next button sits, measured
from the top of the scene. One position means stable.

| Example | Phone (390 px) | Desktop (1100 px) |
|---|---|---|
| ai-harness | **14 positions, 631 to 875 px** | 3 positions, 598 to 693 px |
| langgraph | 2 positions, 641 to 664 px | **3 positions, 616 to 769 px** |
| flaky-test | stable | 3 positions, 685 to 757 px |
| hash-table, meta example | stable | stable |

LangGraph, step 8 to step 9 (the "slide 9" bug) at desktop width: the deck switches from the *chain*
section to the *graph* section, the stage grows from 470 to 603 px, and every control drops 133 px.
After that, each lap of "ask for a tool" adds a row to the message list, so the controls drop another
20 px per step (723 px stage after three laps).

### Root causes

The stage has no size of its own. It is exactly as tall as whatever is drawn in it right now, and the
caption and controls sit directly below it. Four things change that height:

1. **Deck sections differ in height.** Only the active section is in the layout (`display:none` on the
   rest), so switching section resizes the stage. This is the LangGraph step 9 jump.
2. **Content grows inside a section.** Lists, logs and message histories get longer as steps advance
   (LangGraph's message list, ai-harness on a phone).
3. **Captions wrap to more lines than reserved.** `.caption` has a fixed `min-height` in `em`; a longer
   caption, or a narrow phone, spills past it (LangGraph step 11 on a phone: +23 px).
4. **The step dots change layout.** When a reader's choice pushes the step count past 12, `.dots` switches
   to the full-width bar style and the controls row gets 17 px taller.

Authors patch this by hand today (`#manual .stage{min-height:460px}` in ai-harness), which breaks at
another width, font or theme.

### Fix: reserve the space, then forbid growth

The player owns the size of the stage, the caption and the controls. Content adapts to the box, not the
other way round.

**a. Stack deck sections in one grid cell (CSS only).**
All sections share one cell; inactive ones are `visibility:hidden` instead of `display:none`. The cell is
as tall as the tallest section, so switching section changes nothing outside the stage.

```css
.scene.deck .stage{display:grid}
.scene.deck [data-scene]{grid-area:1/1;visibility:hidden;opacity:0}
.scene.deck [data-scene].on{visibility:visible;opacity:1}
```

Hidden sections keep their focusable elements out of tab order with `inert`.

Tried on LangGraph by injecting this CSS: at desktop width, steps 1 to 8 now sit at the graph's height
(Next at 732 px for all of them), so the step 9 jump is gone. What still moves (+17 px when the choice
buttons appear, +20 px per message row, +23 px for one long caption on a phone) is causes 2 to 4, which
the next three parts handle.

**b. Measure every step once, reserve the tallest (player).**
After `setup()` and before first paint, the player draws every step without animation, records the
stage and caption heights, and sets the largest as `min-height` through two custom properties:
`--stage-h` and `--caption-h`. It measures again (grow only, never shrink mid-session) when:

- fonts finish loading (`document.fonts.ready`),
- the width changes (debounced `ResizeObserver` on the figure; a real width change may shrink),
- `setSteps()` or `branch()` adds steps. If the new steps need more room, the stage grows once, at the
  moment of the reader's own action, never during Next or Play.

This replaces every hand-set `min-height`. For 10 to 25 steps the measuring pass costs a few
milliseconds. `api.reserve()` lets a scene ask for a re-measure after async work.

**c. Give growing content a fixed well.**
Anything that grows with the steps (message lists, logs, queues, timelines with many rows) goes in a
`.well`: a box with a fixed height (default about 6 rows) that scrolls inside and keeps the newest row in
view. `api.well(el)` wires the auto-scroll. The page outside the well never sees the growth.

**d. Fix the small things.**
- Dots: choose the dot style once from the largest step count the scene can reach (or always use the
  bar on a phone), and give the dots row a fixed height.
- Caption: the reserved height in (b) covers the longest caption; the 200-character rule keeps it sane.
- The speed menu already opens *below* the buttons, so it never moves them. Keep that rule for any
  future control.

**e. Phone: keep the controls in reach.**
At phone width, when the scene is taller than the viewport, the caption and controls become a dock with
`position:sticky; bottom:0`, so the reader never scrolls to find Next. A stage budget keeps this rare:
the reserved stage should fit in about 60% of an 844 px tall phone screen; above that the check prints
a note.

**Result:** stage, caption and controls have one height per width. Back, Next and Play have one position
per width for the whole scene.

---

## 2. Page anatomy, written in the HTML

The model already learns by copying HTML: it starts from `templates/page.src.html` and imitates the
examples. So the anatomy lives in the template as real markup, not as a table in a markdown file. Each
part is an element with a `data-slot` name, a class the player styles, and a one-line comment saying
what goes there. The model fills it in or deletes it.

Today the template has a hook, one scene and a payoff, and each example invents its own prose and
sources markup (`.sources`, `.src`, a bare `<h2>`). The new template carries every slot, in order:

```html
<body data-kind="concept">            <!-- concept | pr | incident | onboarding -->

<header class="masthead col" data-slot="masthead">   <!-- optional: kind label + theme toggle -->
  <span class="kind">Pull request</span>
  <button type="button" data-theme-toggle>Day / Night</button>
</header>

<main>
  <header class="col stack" data-slot="intro">
    <h1 class="hook">HEADLINE: one question the reader cannot answer yet?</h1>        <!-- required -->
    <p class="dek">HOOK: one or two sentences the reader already knows.</p>          <!-- required -->
    <p class="meta">5 min read · checked against v1.2 on 14 Nov 2026</p>          <!-- optional -->
  </header>

  <dl class="tldr col" data-slot="summary">          <!-- optional: label and value pairs -->
    <dt>What</dt><dd>…</dd>
    <dt>Why</dt><dd>…</dd>
  </dl>

  <section class="wide" data-slot="scene">           <!-- required: the stepper -->
    <figure class="scene" id="main"><div class="stage">…</div></figure>
  </section>

  <section class="col stack" data-slot="payoff">     <!-- required -->
    <p class="payoff">PAYOFF: the one sentence to <mark>remember</mark>.</p>
  </section>

  <section class="prose col" data-slot="prose">      <!-- optional, up to 3 -->
    <h2>Where you will see this</h2>
    <p>Short paragraph. Current facts cite a source: <a class="cite" href="#src-1">[1]</a></p>
  </section>

  <dl class="glossary col" data-slot="glossary">…</dl>    <!-- optional -->

  <section class="sources col" data-slot="sources">  <!-- required when facts are current -->
    <h2>Sources</h2>
    <ol><li id="src-1"><a href="https://…">Title</a>, version or date</li></ol>
  </section>

  <nav class="next col" data-slot="next">…</nav>     <!-- optional: the PR, the runbook, the next part -->
</main>
```

Rules, also written as comments in the template:

- **Order is fixed, slots are optional.** Delete a slot, never move it, so every explainer reads the same way.
- **Words in the reading column, the scene wide.** Everything but the scene uses `.col` (66ch); on a
  phone both are full width minus a 16 px gutter.
- **Citations are links.** `<a class="cite" href="#src-2">[2]</a>` in prose or a caption, pointing at
  `<li id="src-2">` with a real URL and, for current tech, a version or date.
- **Word budget stays:** 150 to 400 words outside the scene.

`data-slot` is what makes the page checkable: the check script reads the slots instead of guessing from
class names, and themes can target `[data-slot=masthead]` safely.

---

## 3. Use cases as HTML starters

Each use case gets a starter page next to the base template, a complete working `.src.html` the model
copies, with neutral placeholder content:

```
templates/
  page.src.html            base: every slot, generic placeholders
  kinds/
    concept.src.html       hook → mechanism scene → "Where you will see this"
    pr.src.html            tldr: What / Why / Risk / How to test; before-and-after scene; "What to review"
    incident.src.html      tldr: Impact / Duration / Cause / Status; timeline scene; "What we changed"
    onboarding.src.html    tldr: You will learn / You need; glossary; "Next part" nav
```

A starter is the base template with the right slots kept, the headings written, and a scene skeleton of
the right shape (a before/after toggle for a PR, a timeline deck for an incident). It builds and passes
the check as shipped, so the model starts from something that works and only replaces content.

| Starter | Masthead | Summary (`tldr`) | Scene shape | Reader action | Prose | Extra slots |
|---|---|---|---|---|---|---|
| concept | none | none | the mechanism | choose an input | "Where you will see this" | sources if current |
| pr | "Pull request" | What, Why, Risk, How to test | before and after | toggle old and new path | "What changed", "What to review" | next: link to the PR |
| incident | "Incident review" | Impact, Duration, Cause, Status | timeline, then the failure path | choose where to intervene | "What we changed", "Follow-ups" | sources: postmortem (no hosts or names) |
| onboarding | "Part 2 of 5" | You will learn, You need | one system, step by step | try a route | "Try it yourself" | glossary, next part |

The examples stay the place to learn *style* (LangGraph, ai-harness, the meta example); the starters
are the place to learn *structure*. A new kind (design review, migration guide) is one new starter file,
not new player code.

To keep the starters from drifting, the check script compares each starter's slot order with the base
template, and CI builds and checks all of them.

---

## 4. What changes where

### Player (`player.js`, `player.css`)

- Grid-stacked deck sections, `inert` on hidden ones (1a).
- Measure-and-reserve pass, `--stage-h` and `--caption-h`, `api.reserve()` (1b).
- `.well` class and `api.well(el)` (1c).
- Dots style chosen once; fixed dots row height (1d).
- Sticky dock at phone width (1e).
- Base styles for the new slots: `.masthead`, `.dek`, `.meta`, `.tldr`, `.prose`, `.glossary`,
  `.sources`, `.cite`, `nav.next`. Layout and spacing only; color and type come from the theme.
- Expose layout facts for the check: `__explainer.layout = { stageH, captionH, controlsY }` per scene.
- A version string, `Explainer.version`, so the check and old pages can tell which player built them.

### Themes

- No layout. A theme sets tokens and may restyle chrome (borders, the masthead strip, the stamp), but
  never sets `height`, `min-height`, `padding` or `display` on `.stage`, `.caption`, `.controls` or
  `[data-scene]`. The reservation depends on that.
- Optional tokens for the new slots, with sensible fallbacks so existing themes keep working:
  `--dek-scale`, `--tldr-bg`, `--cite-color`.
- Each theme's header comment lists how it styles the masthead (Flight Deck's strip, Transit's line
  badge), so the starters look native in every theme.

### `SKILL.md`

Stays short and points at HTML instead of describing it:

- Step 3 says: copy `templates/kinds/<kind>.src.html` (or `page.src.html` for anything else), keep the
  slots you need, delete the rest. One line per kind, no anatomy tables.
- The build rules gain three lines: growing content goes in a `.well`; never set a height on the stage;
  cite current facts with `.cite` links into `.sources`.
- Add the new class names to the reserved list.
- `references/story-beats.md` keeps the writing advice; anything about structure moves into template comments.

### `check.mjs`

New failures:

- **Controls moved.** The Next button's position, relative to the scene, differs between any two steps
  at the same width (1 px tolerance). Reported as "controls moved 133 px between step 8 and step 9".
- **Reserve exceeded.** A step's stage or caption is taller than the reserved height (content escaped a
  well, or a draw added rows the measuring pass did not see).
- **Anatomy.** Missing a required slot (`intro` with `h1.hook` and `p.dek`, `scene`, `payoff`), slots out of
  order, or more than one `h1`. A starter whose slot order differs from the base template.
- **Broken citations.** A `.cite` pointing at a missing `id`, or a source without an `http(s)` link.
- **Theme overrides layout.** A computed `min-height` or `height` on `.stage` that the player did not set.

New notes (not failures):

- The reserved stage is taller than 60% of a phone screen.
- The page links to outside docs but has no Sources section.
- More than 400 words outside the scene.

New option: `--click <selector>` clicks reader buttons (repeatedly, until disabled) and keeps walking, so
branches are measured too. This is the open item from the first dogfood run, and the LangGraph growth
only shows up after a choice.

---

## 5. Rollout

Three changes, each small enough to review on a phone:

1. **Stability.** Player 1a to 1e, the "controls moved" and "reserve exceeded" checks, `--click`.
   Migrate LangGraph (message list into a well) and ai-harness (drop the hand-set `min-height`). Done
   when every example reports one Next position per width.
2. **Anatomy.** Slot styles, the base template with every slot, citation and anatomy checks.
   Move the existing examples' sources and prose into the shared slots.
3. **Starters.** The four `templates/kinds/*.src.html` files, then one dogfood run per new kind (a PR and an incident,
   with neutral made-up content) logged in `runs.csv`.

## Open questions

- **Sticky dock on a phone:** worth it, or does a stage budget alone keep controls on screen? I lean
  towards the dock, since tall decks like ai-harness will exist anyway.
- **Captions above or below the stage:** below today. Above would keep the text next to the headline
  and leave the controls as the only thing at the bottom. Worth trying on one example.
- **Several scenes per page** (onboarding with chapters): allowed today; keep it, but the starters assume
  one, and the check measures each scene on its own.
