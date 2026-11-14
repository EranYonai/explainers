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
 */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var reduce = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  var registry = (window.__explainer = window.__explainer || { scenes: [], errors: [] });
  if (reduce) document.documentElement.classList.add("reduce-motion");

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
    var caption = h("p", { class: "caption", "aria-live": "polite" }, fig);
    var bar = h("div", { class: "controls" }, fig);
    var prev = h("button", { type: "button", class: "prev", text: "Back" }, bar);
    var next = h("button", { type: "button", class: "next primary", text: "Next" }, bar);
    var play = h("button", { type: "button", class: "play", text: "Play" }, bar);
    var dots = h("div", { class: "dots", "aria-hidden": "true" }, bar);

    var steps = [], idx = 0, timer = null, state = {};
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
      // Replace the steps, e.g. after the reader picks an input and real code generates a new trace.
      setSteps: function (s, at) { steps = s || []; buildDots(); stop(); show(at || 0, true); },
      // Keep steps up to the current one, replace everything after it, and move on: a reader's choice
      // that changes what happens next (pick a route, approve a call).
      branch: function (s) { steps = steps.slice(0, idx + 1).concat(s || []); buildDots(); stop(); show(idx + 1, true); },
      // Jump to the first step that matches, e.g. api.goWhere(function (s) { return s.scene === "panel"; }).
      goWhere: function (pred) { for (var i = 0; i < steps.length; i++) if (pred(steps[i], i)) { stop(); show(i, true); return i; } return -1; },
      redraw: function () { show(idx, false); },
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
          if (!quiet) report(name, "caption needs {" + key + "} but compute() and state do not provide it");
          return "[?" + key + "]";
        }
        return fmt(v);
      });
    }

    function buildDots() {
      dots.innerHTML = "";
      dots.classList.toggle("many", steps.length > 12);
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
        names.forEach(function (n) { sections[n].classList.toggle("on", n === sc); });
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
      setCaption(fill(steps[idx].say, state));
      for (var d = 0; d < dots.children.length; d++) {
        dots.children[d].classList.toggle("on", d === idx);
        dots.children[d].classList.toggle("done", d < idx);
      }
      prev.disabled = idx === 0;
      next.textContent = idx === steps.length - 1 ? "Restart" : "Next";
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
      }, holdFor(steps[idx]));
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
    show(0, false);
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

  window.Explainer = { scene: scene, svg: svg, h: h, rng: rng, fmt: fmt, reduce: reduce };
})();
