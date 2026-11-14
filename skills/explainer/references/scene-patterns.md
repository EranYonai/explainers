# Scene patterns

Patterns from the explainers that worked. Each is a section in a deck (`<section data-scene=... data-title=...>`)
with a `setup` that builds its DOM once and a `draw(state)` that toggles classes. Prefer HTML (cards, bubbles,
lists, buttons) over SVG; use SVG only for real diagrams.

## Player recap

```js
var api = Explainer.scene("#main", {
  title: "For screen readers",
  initial: { focus: -1 },
  steps: [
    { scene: "parts", say: "There are {count} parts.", set: { focus: -1 } },
    { scene: "parts", say: "This one routes requests.", set: { focus: 0 } },
    { scene: "choose", say: "Your turn.", wait: true },
  ],
  compute: function (s) { return { count: PARTS.length }; },
  scenes: { parts: { setup: function (el, api) {}, draw: function (s, api) {} } }
});
```

- `set` carries forward, `mark` lasts one step. `draw` must work from any step (Back, jumps), so it sets every
  class it owns, every time.
- `api.branch(steps)` replaces what comes after the current step: use it for any reader choice.
- `api.say(text)` replaces the caption after a click inside a scene. `api.goWhere(fn)` jumps (tabs).
- Reader input that should NOT advance (answering several questions on one step): keep the answers in a
  variable of your own, rebuild the steps from them, and call `api.setSteps(makeSteps(answers), api.index)`.
  `api.state` is derived from the steps and read-only; never write to it.
- Give every scene section the same `min-height` (e.g. `#main .stage{min-height:420px}`) so controls do not jump.
- `api.rng(seed)` for anything random. `api.h(tag, attrs, parent)` and `api.svg(...)` build elements.
- `<button data-theme-toggle>` anywhere on the page flips light and dark.

## Patterns

**Stations (a process or loop).** An `<ol>` of steps; `draw` adds `.on` to `state.k`. Pair it with a
"tape" panel that fills as the process runs: rows with `data-at`, hidden while `at > k`.

**Chat (an interview, an agent, a support thread).** Bubbles in a column. State is how many are visible;
`draw` shows the first `n` and pops the newest. Name who speaks with a small tag, not color alone.

**Proposal and decision (the reader approves).** A card with the proposed action, its risk, and
Approve / Deny buttons. Each click appends to a log the model "sees next" and computes the consequence with
real logic. End with a debrief that depends on what the reader did. Mark the step `wait: true`.

**Switch panel (what if this part were missing).** A grid of toggle buttons (`aria-pressed`). Pulling one
shows its fault in a readout; a master line summarizes how many are fitted. Steps walk through each switch
with `set: { focus: i }`; the reader can then play freely.

**Tabs comparison (three tools, three approaches).** Tabs with `role="tab"` and cards; on a phone show one
card, on desktop show all and highlight the active. Clicking a tab jumps with `api.goWhere`.

**Route choice (a graph or state machine).** Draw the graph; at a junction show choice buttons. Each choice
calls `api.branch(routeSteps(choice))` where `routeSteps` walks the real graph and writes the captions.

**Slider component (a quantity the reader varies).** A pure function `model(params, seed) -> outputs`.
The slider sets params, the page shows outputs, captions read them via `compute`. No `Math.random`.

**Worked numbers.** When a step states a number, generate it: run the algorithm in a function, store the
result in state, and write `{name}` in the caption.

## Layout

- The stage is a column on a phone. Use `grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr))`
  or a `@media (min-width: 760px)` two-column split. Never a fixed width.
- Keep every scene in a deck about the same height so the controls do not jump; set a `min-height` on the stage.
- Text in SVG: viewBox about 360 wide on a phone; labels at least 12 units; hide secondary labels on narrow
  screens instead of shrinking them.
