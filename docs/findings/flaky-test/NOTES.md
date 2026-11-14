# Field notes: "Why a flaky test lies"

**Where the line fell.** The two-run timeline is pure states: 8 steps, each one `now N` plus a cell value. The line sits at "one run vs many". One interleaving is a state. 200 random ones are a distribution, and no author can write those as steps. No trace: a real race cannot be reproduced on demand, so the timings are hand-picked.

**The component is smaller than expected.** Only the dot plot is custom JS (about 60 lines). Sliders, stat tiles, run grid and captions are engine primitives fed by component *outputs*, so the contract is two-way: typed params in, named outputs out.

**Typed params.** `work_ms`, `sleep_ms`, `jitter_ms` (number, ms), `wait` (enum sleep|join), `runs` (int), `seed` (int), `progress` (number 0..1). Outputs: `failed`, `shown`, `rate`, `expected_rate`, `red_after_retries`, `avg_test_ms`, `results[]`. The component is a pure function `update(params) -> outputs`: no internal clock, no `Math.random`.

**Wiring.** `controls:` declares sliders with ids; `params: { jitter_ms: { bind: jitter } }` connects them. Steps stay states: `do: [set jitter 10]`, and the engine tweens the number so the dots slide. Dragging a slider drops into `free-play`.

**Primitives.** timeline with lanes, numeric `cursor`, spans that fill to the cursor, spans with gaps, cell, stamp, stat, run-grid, slider, choice. Wished: `reset` between runs, `check:` invariants.

**What YAML could not express.** Captions with numbers nobody knows at writing time (`{sim.failed}`), so captions need output templating. Derived state: `saved` is really `now >= 40`, and writing both invites drift. Responsive layout: I set the viewBox to the measured pixel width so text stays 12px on a phone. Arrow keys clash with a focused slider.

**Compiler: saved / in the way.** Saved: stepper, tweening, controls, tiles, theme, layout, about 70% of the file. In the way: label fitting inside short bars, and where the hand-drawn filter applies (shapes yes, text no).

**What an AI author gets wrong.** Captions that contradict the sample ("Still 0 of 200 fail"); symmetric Gaussian jitter, which makes work finish early; hardcoded counts; a seed that happens to show zero failures at the key step. `check:` on outputs plus the analytic `expected_rate` catches all four.

**9:16 silent reel.** Hook card 4s, scene 1 at 4s per step, scene 2 at 6s per step, payoff card 5s: about 75s. Large caption in the lower third, scene above. The random component works in fixed video because it is seeded: the reel records seed 11, the engine tweens `progress` so dots rain in, then tweens slider values between steps with the slider drawn moving by itself. Same frames every render.

**Verdict.** The three layers hold, provided components are pure, seeded, and return outputs that captions and primitives can bind to.
