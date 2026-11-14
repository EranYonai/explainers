/* explainer player v0
 * One shared stepper for every explainer: Back / Next / Play, captions, dots, keys, reduced motion.
 * A scene is data plus two small functions:
 *
 *   Explainer.scene("#queue", {
 *     title: "Requests waiting in a queue",        // used for the stage's aria-label
 *     initial: { waiting: 0, served: 0 },          // state before step 1
 *     steps: [                                     // or a function (api) -> steps, see setSteps
 *       { say: "Three requests arrive at once.", set: { waiting: 3 } },
 *       { say: "The worker takes one. {left} still wait.", set: { waiting: 2, served: 1 }, mark: { busy: true } },
 *     ],
 *     setup(stage, api) { ... },                   // build the DOM once
 *     draw(state, api)  { ... },                   // make the DOM match `state`; api.animate is false on first paint
 *     compute(state)    { return { left: state.waiting }; }  // numbers for {name} in captions
 *   });
 *
 * Deck mode (one stepper drives several sections, like a manual): put <section data-scene="loop" data-title="The loop">
 * blocks inside the figure, give each step `scene: "loop"`, and pass per-section code as
 * `scenes: { loop: { setup(sectionEl, api), draw(state, api) } }`. Only the active section is shown.
 * A step with `wait: true` stops Play there, because the reader has something to do.
 *
 * State at step i = initial, then every step's `set` from 0..i merged in order, then step i's `mark`.
 * `set` carries forward; `mark` is true for one step only (highlights, "look here", a probe).
 * Captions may use {name}: filled from compute(state), then state. A missing name renders [?name] and is
 * reported in window.__explainer.errors, so the check script fails instead of shipping a wrong number.
 *
 * Layout is steady: the player draws every step once, then reserves the tallest stage and caption, so
 * Back / Next / Play never move between steps. Deck sections share one grid cell (the tallest wins).
 * Content that grows with the steps (a message list, a log) goes in an element with class "well":
 * a fixed-height box that scrolls inside; api.well(el) keeps its newest row in view.
 * Call api.reserve() if a scene changes size after async work.
 * If a reader's choice adds steps (api.branch), list every outcome up front so they are measured too:
 *   branches: function (api) { return CHOICES.map(function (c, i) { return outcome(i); }); }
 */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var reduce = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  var VERSION = "1";
  var registry = (window.__explainer = window.__explainer || { scenes: [], errors: [], version: VERSION });
  if (reduce) document.documentElement.classList.add("reduce-motion");

  // Playback speed, shared by every scene on the page and remembered per viewer.
  var SPEEDS = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];
  var speed = 1, speedViews = [];
  try { var saved = parseFloat(localStorage.getItem("explainer-speed")); if (SPEEDS.indexOf(saved) >= 0) speed = saved; } catch (e) {}
  function speedLabel(v) { return v + "\u00d7"; }
  function setSpeed(v) {
    speed = v;
    try { localStorage.setItem("explainer-speed", String(v)); } catch (e) {}
    speedViews.forEach(function (f) { f(); });
  }

  function report(scene, msg) {
    registry.errors.push(scene + ": " + msg);
    if (window.console) console.error("[explainer] " + scene + ": " + msg);
  }

  function svg(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) if (attrs[k] != null) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  function h(tag, attrs, parent) {
    var e = document.createElement(tag);
    for (var k in attrs) {
      if (k === "text") e.textContent = attrs[k];
      else if (attrs[k] != null) e.setAttribute(k, attrs[k]);
    }
    if (parent) parent.appendChild(e);
    return e;
  }

  // Seeded random numbers (mulberry32): same seed, same sequence, so captions and videos stay stable.
  function rng(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6d2b79f5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function fmt(v) {
    return typeof v === "number" ? v.toLocaleString("en-US", { maximumFractionDigits: 2 }) : String(v);
  }

  function words(s) {
    return String(s || "").split(/\s+/).filter(Boolean).length;
  }

  // Hand-drawn wobble: one shared SVG filter, strength from the theme's --sketch token (0 = off).
  var roughDone = false;
  function ensureRough() {
    if (roughDone) return;
    roughDone = true;
    var scale = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--sketch")) || 0;
    var defs = svg("svg", { width: 0, height: 0, "aria-hidden": "true", style: "position:absolute" }, document.body);
    var f = svg("filter", { id: "rough", x: "-5%", y: "-5%", width: "110%", height: "110%" }, svg("defs", {}, defs));
    svg("feTurbulence", { type: "fractalNoise", baseFrequency: "0.035", numOctaves: 2, seed: 7, result: "n" }, f);
    svg("feDisplacementMap", { in: "SourceGraphic", in2: "n", scale: scale, xChannelSelector: "R", yChannelSelector: "G" }, f);
  }

  function scene(target, opts) {
    var fig = typeof target === "string" ? document.querySelector(target) : target;
    var name = fig && (fig.id || opts.title) || "scene";
    if (!fig) { report(String(target), "element not found"); return null; }
    ensureRough();

    fig.classList.add("scene");
    if (!fig.hasAttribute("tabindex")) fig.setAttribute("tabindex", "0");
    var stage = fig.querySelector(".stage") || h("div", { class: "stage" }, fig);
    stage.setAttribute("role", "img");
    stage.setAttribute("aria-label", opts.title || name);
    var sections = {}, head = null;
    [].forEach.call(fig.querySelectorAll("[data-scene]"), function (s) { sections[s.getAttribute("data-scene")] = s; });
    var names = Object.keys(sections);
    if (names.length) {
      fig.classList.add("deck");
      head = h("div", { class: "sec" }, null);
      stage.parentNode.insertBefore(head, stage);
    }
    // Caption and controls share a dock: below the stage, sticky at the bottom of a phone screen.
    var dock = h("div", { class: "dock" }, fig);
    var caption = h("p", { class: "caption", "aria-live": "polite" }, dock);
    var bar = h("div", { class: "controls" }, dock);
    var prev = h("button", { type: "button", class: "prev", text: "Back" }, bar);
    var next = h("button", { type: "button", class: "next primary", text: "Next" }, bar);
    // Play is a split control: the main part plays and pauses, the chip shows the speed and opens the choices.
    var group = h("div", { class: "playgroup" }, bar);
    var play = h("button", { type: "button", class: "play", text: "Play" }, group);
    var chip = h("button", { type: "button", class: "speed-now", "aria-expanded": "false", "aria-label": "Playback speed" }, group);
    var menu = h("div", { class: "speed-menu", role: "group", "aria-label": "Playback speed", "aria-hidden": "true" }, bar);
    var menuIn = h("div", { class: "speed-opts" }, menu);
    var opts_ = SPEEDS.map(function (v) {
      var b = h("button", { type: "button", "data-speed": v, tabindex: "-1", text: speedLabel(v) }, menuIn);
      b.addEventListener("click", function () { setSpeed(v); openMenu(false); chip.focus(); if (timer) { clearTimeout(timer); tick(); } });
      return b;
    });
    function paintSpeed() {
      chip.textContent = speedLabel(speed);
      chip.setAttribute("aria-label", "Playback speed " + speedLabel(speed) + ". Change");
      opts_.forEach(function (b) { b.setAttribute("aria-pressed", +b.getAttribute("data-speed") === speed); });
    }
    function openMenu(on) {
      fig.classList.toggle("speed-open", on);
      chip.setAttribute("aria-expanded", on);
      menu.setAttribute("aria-hidden", !on);
      opts_.forEach(function (b) { b.setAttribute("tabindex", on ? "0" : "-1"); });
      if (on) { var cur = opts_[SPEEDS.indexOf(speed)]; if (cur) cur.focus(); }
    }
    chip.addEventListener("click", function () { openMenu(chip.getAttribute("aria-expanded") !== "true"); });
    menu.addEventListener("keydown", function (e) {
      var i = opts_.indexOf(document.activeElement);
      if (e.key === "Escape") { openMenu(false); chip.focus(); }
      else if ((e.key === "ArrowRight" || e.key === "ArrowLeft") && i >= 0) {
        opts_[(i + (e.key === "ArrowRight" ? 1 : opts_.length - 1)) % opts_.length].focus();
      } else return;
      e.preventDefault(); e.stopPropagation();
    });
    speedViews.push(paintSpeed);
    paintSpeed();
    var dots = h("div", { class: "dots", "aria-hidden": "true" }, bar);

    var steps = [], idx = 0, timer = null, state = {};
    var reserved = { stage: 0, caption: 0 }, maxCount = 0, lastWidth = 0;
    var api = {
      el: fig, stage: stage, reduce: reduce, animate: false,
      get index() { return idx; },
      get count() { return steps.length; },
      get state() { return state; },
      get step() { return steps[idx]; },
      get scene() { return steps[idx] && steps[idx].scene; },
      sections: sections,
      go: function (i) { stop(); show(i, true); },
      next: function () { stop(); step(1); },
      prev: function () { stop(); step(-1); },
      play: function () { if (!timer) toggle(); },
      stop: stop,
      get speed() { return speed; },
      setSpeed: setSpeed,
      // Replace the steps, e.g. after the reader picks an input and real code generates a new trace.
      setSteps: function (s, at) { steps = s || []; buildDots(); stop(); reserve(false); show(at || 0, true); },
      // Keep steps up to the current one, replace everything after it, and move on: a reader's choice
      // that changes what happens next (pick a route, approve a call).
      branch: function (s) { steps = steps.slice(0, idx + 1).concat(s || []); buildDots(); stop(); reserve(false); show(idx + 1, true); },
      // Jump to the first step that matches, e.g. api.goWhere(function (s) { return s.scene === "panel"; }).
      goWhere: function (pred) { for (var i = 0; i < steps.length; i++) if (pred(steps[i], i)) { stop(); show(i, true); return i; } return -1; },
      redraw: function () { show(idx, false); },
      // Measure every step again and reserve the tallest (grow only). Use after async content changes size.
      reserve: function () { reserve(false); },
      // A box that grows with the steps: keep it at a fixed height and its newest row in view.
      well: function (el) { return well(el); },
      get layout() { return { stage: reserved.stage, caption: reserved.caption, dots: dots.classList.contains("many") ? "bar" : "dots" }; },
      // Replace the caption until the next step, e.g. after the reader clicks something inside a scene.
      say: function (text) { setCaption(text); },
      stateAt: stateAt,
      captionAt: function (i) { return fill(steps[i] && steps[i].say, stateAt(i), true); },
      svg: svg, h: h, rng: rng
    };

    function stateAt(i) {
      var s = {}, k;
      for (k in opts.initial || {}) s[k] = opts.initial[k];
      for (var j = 0; j <= i && j < steps.length; j++) for (k in steps[j].set || {}) s[k] = steps[j].set[k];
      var m = (steps[i] && steps[i].mark) || {};
      for (k in m) s[k] = m[k];
      return s;
    }

    function fill(text, s, quiet) {
      var vals = opts.compute ? opts.compute(s, api) || {} : {};
      return String(text || "").replace(/\{(\w+)\}/g, function (all, key) {
        var v = key in vals ? vals[key] : s[key];
        if (v === undefined || v === null || (typeof v === "number" && !isFinite(v))) {
          if (!quiet && !measuring) report(name, "caption needs {" + key + "} but compute() and state do not provide it");
          return "[?" + key + "]";
        }
        return fmt(v);
      });
    }

    // The dot style is chosen from the most steps this scene has had, so it never flips back and forth.
    function buildDots() {
      dots.innerHTML = "";
      maxCount = Math.max(maxCount, steps.length, steps.length + branchLists().reduce(function (m, b) { return Math.max(m, b.length); }, 0));
      dots.classList.toggle("many", maxCount > 12);
      for (var i = 0; i < steps.length; i++) h("i", {}, dots);
    }

    function show(i, animate) {
      if (!steps.length) return;
      idx = Math.max(0, Math.min(steps.length - 1, i));
      state = stateAt(idx);
      api.animate = !!animate && !reduce;
      var sc = steps[idx].scene;
      if (names.length) {
        if (sc && !sections[sc]) report(name, "step " + (idx + 1) + " names scene '" + sc + "' but there is no [data-scene=" + sc + "]");
        names.forEach(function (n) { sections[n].classList.toggle("on", n === sc); sections[n].inert = n !== sc; });
        var pos = names.indexOf(sc) + 1, title = sc && sections[sc] ? sections[sc].getAttribute("data-title") || "" : "";
        head.innerHTML = "";
        h("span", { class: "no", text: pos + " / " + names.length }, head);
        h("span", { class: "ttl", text: title }, head);
      }
      try {
        var part = sc && opts.scenes && opts.scenes[sc];
        if (part && part.draw) part.draw(state, api);
        if (opts.draw) opts.draw(state, api);
      } catch (e) { report(name, "draw() failed at step " + (idx + 1) + ": " + e.message); }
      if (!measuring) scrollWells(api.animate);
      setCaption(fill(steps[idx].say, state));
      for (var d = 0; d < dots.children.length; d++) {
        dots.children[d].classList.toggle("on", d === idx);
        dots.children[d].classList.toggle("done", d < idx);
      }
      prev.disabled = idx === 0;
      next.textContent = idx === steps.length - 1 ? "Restart" : "Next";
    }

    // Draw every step without motion, record the tallest stage and caption, reserve that much.
    // grow only: during a session the box may get taller (after a reader's choice), never shorter,
    // except when the width changes.
    var measuring = false;
    function branchLists() {
      if (typeof opts.branches !== "function") return [];
      try { return (opts.branches(api) || []).filter(function (b) { return b && b.length; }); }
      catch (e) { report(name, "branches() failed: " + e.message); return []; }
    }
    function reserve(allowShrink) {
      if (!steps.length || !fig.isConnected) return;
      var keep = idx, real = steps, sy = window.scrollY, ms = 0, mc = 0;
      // the steps as they are, plus each declared reader outcome added after them
      var runs = [{ list: steps, from: 0 }].concat(branchLists().map(function (b) { return { list: real.concat(b), from: real.length }; }));
      measuring = true;
      fig.classList.add("measuring");
      try {
        runs.forEach(function (run) {
          steps = run.list;
          for (var i = run.from; i < steps.length; i++) {
            show(i, false);
            ms = Math.max(ms, stage.getBoundingClientRect().height);
            mc = Math.max(mc, caption.getBoundingClientRect().height);
          }
        });
      } finally {
        steps = real;
        if (!allowShrink) { ms = Math.max(ms, reserved.stage); mc = Math.max(mc, reserved.caption); }
        reserved.stage = Math.ceil(ms); reserved.caption = Math.ceil(mc);
        fig.style.setProperty("--stage-h", reserved.stage + "px");
        fig.style.setProperty("--caption-h", reserved.caption + "px");
        show(keep, false);
        void fig.offsetHeight;
        fig.classList.remove("measuring");
        measuring = false;
        if (window.scrollY !== sy) window.scrollTo(window.scrollX, sy);
      }
    }

    // Wells scroll to their newest row after every draw.
    var wells = [];
    function well(el) {
      if (!el) return el;
      el.classList.add("well");
      if (wells.indexOf(el) < 0) wells.push(el);
      return el;
    }
    function scrollWells(animate) {
      wells.forEach(function (el) { el.scrollTo({ top: el.scrollHeight, behavior: animate ? "smooth" : "auto" }); });
    }

    function setCaption(text) {
      caption.innerHTML = "";
      h("span", { class: "stepno", text: "step " + (idx + 1) + " of " + steps.length }, caption);
      caption.appendChild(document.createTextNode(text));
    }

    function step(d) {
      if (d > 0 && idx === steps.length - 1) show(0, true);
      else show(idx + d, true);
    }

    function holdFor(s) {
      if (s && s.hold) return s.hold;
      return Math.max(1800, Math.min(7000, 900 + 260 * words(s && s.say)));
    }

    function stop() {
      if (timer) { clearTimeout(timer); timer = null; play.textContent = "Play"; }
    }

    function tick() {
      timer = setTimeout(function () {
        if (idx >= steps.length - 1) { stop(); return; }
        show(idx + 1, true);
        if (steps[idx].wait) { stop(); return; }
        tick();
      }, holdFor(steps[idx]) / speed);
    }

    function toggle() {
      if (timer) { stop(); return; }
      if (idx === steps.length - 1) show(0, true);
      else if (steps[idx].wait) show(idx + 1, true);
      play.textContent = "Pause";
      tick();
    }

    prev.addEventListener("click", function () { stop(); step(-1); });
    next.addEventListener("click", function () { stop(); step(1); });
    play.addEventListener("click", toggle);
    function onKey(e) {
      var t = e.target, tag = t && t.tagName;
      if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA" || (t && t.isContentEditable)) return;
      if (t && t.closest && t.closest(".speed-menu")) return;
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      var k = e.key;
      if (k === "ArrowRight") { stop(); step(1); }
      else if (k === "ArrowLeft") { stop(); step(-1); }
      else if (k === "Home") { stop(); show(0, true); }
      else if (k === "End") { stop(); show(steps.length - 1, true); }
      else return;
      e.preventDefault();
    }
    fig.addEventListener("keydown", onKey);
    api.onKey = onKey;

    try {
      if (opts.setup) opts.setup(stage, api);
      names.forEach(function (n) { var p = opts.scenes && opts.scenes[n]; if (p && p.setup) p.setup(sections[n], api); });
    } catch (e) { report(name, "setup() failed: " + e.message); }
    steps = typeof opts.steps === "function" ? opts.steps(api) : opts.steps || [];
    if (!steps.length) report(name, "no steps");
    buildDots();
    reserve(true);
    show(0, false);
    lastWidth = Math.round(fig.getBoundingClientRect().width);
    // Fonts change text size, and a new width changes everything: measure again (may shrink).
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { reserve(true); });
    if (window.ResizeObserver) {
      var rt = null;
      new ResizeObserver(function () {
        var w = Math.round(fig.getBoundingClientRect().width);
        if (w === lastWidth) return;
        lastWidth = w;
        clearTimeout(rt);
        rt = setTimeout(function () { reserve(true); }, 120);
      }).observe(fig);
    }
    registry.scenes.push({ name: name, api: api });
    return api;
  }

  // With a single scene on the page, arrow keys work from anywhere, not only when the scene has focus.
  document.addEventListener("keydown", function (e) {
    if (registry.scenes.length !== 1 || e.defaultPrevented) return;
    var fig = registry.scenes[0].api.el;
    if (fig.contains(e.target)) return;
    registry.scenes[0].api.onKey(e);
  });

  // Any <button data-theme-toggle> flips between light and dark, overriding the system setting.
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-theme-toggle]");
    if (!b) return;
    var r = document.documentElement;
    var cur = r.getAttribute("data-theme") || (window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    r.setAttribute("data-theme", cur === "dark" ? "light" : "dark");
  });

  window.Explainer = { scene: scene, svg: svg, h: h, rng: rng, fmt: fmt, reduce: reduce, version: VERSION };
})();
