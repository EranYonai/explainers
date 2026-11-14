#!/usr/bin/env node
// Self-check for a built explainer page. One run, one short report, one contact sheet.
//
//   node check.mjs page.html [--sheet contact-sheet.png] [--click "<selector>"]
//
// Renders the page at phone width (390 px, light) and desktop width (1100 px, dark), walks every step of
// every scene, then plays the reader: clicks the reader buttons (--click, default ".choices button") and
// walks the steps they produce. Reports:
//   - JS errors and console errors
//   - player errors: captions asking for a {value} that compute() does not provide, draw() failures
//   - controls that move between steps (the stage, caption or controls row changed height)
//   - a page or theme style overriding the height the player reserves for the stage or caption
//   - sideways scroll on the page, and content wider than its scene, at any step
//   - page parts: missing or out-of-order slots (intro with h1.hook and p.dek, scene, payoff), broken
//     citations (.cite pointing nowhere), sources without a link
//   - captions longer than 200 characters, a stage taller than 60% of a phone screen, more than
//     400 words outside the scene, outside links with no Sources (notes, not failures)
//   - external requests other than Google Fonts
// and writes a contact sheet: every step of every scene at phone width, in one image.
// Exit code: 0 pass, 1 fail, 3 skipped (Playwright not installed).
import { createRequire } from "node:module";
import { resolve, dirname, basename, join } from "node:path";
import { existsSync } from "node:fs";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const page = args.find((a, i) => !a.startsWith("--") && !["--sheet", "--click"].includes(args[i - 1]));
if (!page || !existsSync(page)) {
  console.error('usage: node check.mjs <page.html> [--sheet out.png] [--click "<selector>"]');
  process.exit(2);
}
const clickSel = args.includes("--click") ? args[args.indexOf("--click") + 1] : ".choices button";
// The page parts, in their fixed order. Required ones must be present.
const SLOTS = ["masthead", "intro", "summary", "scene", "payoff", "prose", "glossary", "sources", "next"];
const REQUIRED = ["intro", "scene", "payoff"];
const sheetArg = args.includes("--sheet") ? args[args.indexOf("--sheet") + 1] : null;
const sheet = resolve(sheetArg || join(dirname(page), basename(page, ".html") + ".sheet.png"));

function loadPlaywright() {
  const roots = [process.cwd(), dirname(resolve(page)), import.meta.url.replace("file://", "")];
  if (process.env.NODE_PATH) roots.push(...process.env.NODE_PATH.split(":").map((p) => join(p, "x")));
  for (const r of roots) {
    for (const name of ["playwright", "playwright-core"]) {
      try { return createRequire(r.endsWith("/") ? r : r + "/")(name); } catch {}
    }
  }
  return null;
}
const pw = loadPlaywright();
if (!pw) {
  console.log("SKIP  Playwright not found. To enable the check: npm i -D playwright && npx playwright install chromium");
  process.exit(3);
}

const url = pathToFileURL(resolve(page)).href;
const problems = [];
const notes = [];
const shots = [];
let clicked = 0;

// Runs in the page: layout facts for one scene, and facts about the page parts.
const PAGE_HELPERS = `(() => {
  window.__layoutOf = (api) => {
    const fig = api.el, f = fig.getBoundingClientRect();
    const q = (s) => fig.querySelector(s);
    const hgt = (s) => (q(s) ? Math.round(q(s).getBoundingClientRect().height) : 0);
    const nx = q(".next");
    const lay = api.layout || {};
    const minH = (s) => (q(s) ? parseFloat(getComputedStyle(q(s)).minHeight) || 0 : 0);
    return { y: nx ? Math.round(nx.getBoundingClientRect().top - f.top) : 0, stage: hgt(".stage"), caption: hgt(".caption"),
      controls: hgt(".controls"), reserved: lay.stage || 0, reservedCaption: lay.caption || 0,
      stageMin: Math.round(minH(".stage")), captionMin: Math.round(minH(".caption")) };
  };
  window.__pageFacts = () => {
    const slots = [...document.querySelectorAll("[data-slot]")].map((e) => e.getAttribute("data-slot"));
    const intro = document.querySelector('[data-slot="intro"]');
    const src = document.querySelector('[data-slot="sources"]');
    const cites = [...document.querySelectorAll("a.cite")].map((a) => a.getAttribute("href") || "");
    const brokenCites = cites.filter((h) => !h.startsWith("#") || !src || !src.querySelector(h.replace(/([^#\w-])/g, "\\$1")));
    const bareSources = src ? [...src.querySelectorAll("li")].filter((li) => !li.querySelector('a[href^="http"]')).map((li) => li.textContent.trim().slice(0, 40)) : [];
    const outside = [...document.querySelectorAll('a[href^="http"]')].filter((a) => !(src && src.contains(a)) && !a.closest("nav.next")).length;
    let words = 0;
    for (const sl of document.querySelectorAll("[data-slot]")) if (sl.getAttribute("data-slot") !== "scene") words += sl.innerText.split(/\s+/).filter(Boolean).length;
    return { slots, h1: document.querySelectorAll("h1").length, hook: !!(intro && intro.querySelector("h1.hook")), dek: !!(intro && intro.querySelector(".dek")),
      brokenCites, bareSources, outside, words, hasSources: !!src };
  };
})()`;

// Controls must sit in one place for every step of a scene, at a given width.
const seen = new Map();
function track(tag, scene, where, lay) {
  const key = tag + "|" + scene;
  if (lay.reserved && lay.stageMin !== lay.reserved) problems.push(tag + "  " + scene + ": something overrides the stage height the player reserves (min-height " + lay.stageMin + "px, reserved " + lay.reserved + "px). Remove height and min-height rules on .stage.");
  if (lay.reservedCaption && lay.captionMin !== lay.reservedCaption) problems.push(tag + "  " + scene + ": something overrides the caption height the player reserves (min-height " + lay.captionMin + "px, reserved " + lay.reservedCaption + "px). Remove min-height rules on .caption.");
  const first = seen.get(key);
  if (!first) { seen.set(key, { where, lay }); return; }
  if (Math.abs(lay.y - first.lay.y) > 1) {
    const why = [];
    if (lay.stage !== first.lay.stage) why.push("stage " + first.lay.stage + " to " + lay.stage + "px: put growing content in a .well");
    if (lay.caption !== first.lay.caption) why.push("caption " + first.lay.caption + " to " + lay.caption + "px");
    if (lay.controls !== first.lay.controls) why.push("controls row " + first.lay.controls + " to " + lay.controls + "px");
    problems.push(tag + "  " + scene + ": controls moved " + (lay.y - first.lay.y) + "px between " + first.where + " and " + where + (why.length ? " (" + why.join("; ") + ")" : ""));
  }
}

function pageChecks(f) {
  for (const r of REQUIRED) if (!f.slots.includes(r)) problems.push("page part missing: data-slot=\"" + r + "\"");
  const known = f.slots.filter((s) => SLOTS.includes(s));
  const order = known.map((s) => SLOTS.indexOf(s));
  if (order.some((v, i) => i && v < order[i - 1])) problems.push("page parts out of order: " + known.join(", ") + " (order is " + SLOTS.join(", ") + ")");
  f.slots.filter((s) => !SLOTS.includes(s)).forEach((s) => problems.push("unknown page part: data-slot=\"" + s + "\""));
  if (f.slots.includes("intro") && !f.hook) problems.push("the intro needs the headline as h1.hook");
  if (f.slots.includes("intro") && !f.dek) problems.push("the intro needs a short hook as p.dek");
  if (f.h1 !== 1) problems.push("the page has " + f.h1 + " h1 elements; use one, the headline");
  f.brokenCites.forEach((h) => problems.push("citation " + h + " points at no source in the Sources part"));
  f.bareSources.forEach((s) => problems.push("source without a link: " + s));
  if (f.outside && !f.hasSources) notes.push("the page links to outside pages but has no Sources part");
  if (f.words > 400) notes.push(f.words + " words outside the scene; aim for 150 to 400");
}

async function walk(browser, width, scheme, capture) {
  const ctx = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: scheme, reducedMotion: "reduce", deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  const tag = width + "px " + scheme;
  p.on("pageerror", (e) => problems.push(tag + "  JS error: " + e.message));
  p.on("console", (m) => { if (m.type() === "error") problems.push(tag + "  console: " + m.text().slice(0, 160)); });
  p.on("request", (r) => {
    const u = r.url();
    if (!/^(file:|data:|about:|blob:)/.test(u) && !/fonts\.(googleapis|gstatic)\.com/.test(u)) problems.push(tag + "  external request: " + u.slice(0, 100));
  });
  await p.goto(url, { waitUntil: "load" });
  await p.waitForTimeout(400);
  // The phone dock sticks to the bottom of the screen; measure and photograph it in place instead.
  await p.addStyleTag({ content: ".scene .dock{position:static!important}" });
  await p.evaluate(PAGE_HELPERS);
  const count = await p.evaluate(() => (window.__explainer ? window.__explainer.scenes.length : -1));
  if (count < 0) { problems.push(tag + "  no player found (window.__explainer missing)"); await ctx.close(); return 0; }
  let steps = 0;
  for (let s = 0; s < count; s++) {
    const n = await p.evaluate((s) => window.__explainer.scenes[s].api.count, s);
    for (let i = 0; i < n; i++) {
      const r = await p.evaluate(async ([s, i]) => {
        const { name, api } = window.__explainer.scenes[s];
        api.go(i);
        await new Promise((ok) => setTimeout(ok, 60));
        const fig = api.el, fr = fig.getBoundingClientRect();
        let wide = null;
        for (const el of fig.querySelectorAll("*")) {
          if (el.closest(".dots") || getComputedStyle(el).display === "none") continue;
          const b = el.getBoundingClientRect();
          if (b.width && (b.right > fr.right + 1 || b.left < fr.left - 1)) {
            // allow children of horizontally scrollable boxes
            let p = el.parentElement, scroll = false;
            while (p && p !== fig) { if (/(auto|scroll)/.test(getComputedStyle(p).overflowX)) { scroll = true; break; } p = p.parentElement; }
            if (!scroll) { wide = (el.className && el.className.baseVal !== undefined ? el.tagName : el.tagName + "." + el.className) + " " + Math.round(b.right - fr.right) + "px"; break; }
          }
        }
        const cap = fig.querySelector(".caption");
        const text = cap ? cap.textContent.replace(/^step \d+ of \d+/, "") : "";
        return { name, scroll: document.documentElement.scrollWidth - innerWidth, wide, len: text.length, scene: api.scene, lay: window.__layoutOf(api) };
      }, [s, i]);
      const where = tag + "  " + r.name + " step " + (i + 1);
      if (r.scroll > 0) problems.push(where + ": page scrolls sideways by " + r.scroll + "px");
      if (r.wide) problems.push(where + ": content wider than the scene (" + r.wide + ")");
      if (r.len > 200) notes.push(where + ": caption is " + r.len + " characters; aim for under 200");
      track(tag, r.name, "step " + (i + 1), r.lay);
      if (capture && width === 390 && r.lay.reserved > 0.6 * 844 && i === 0) notes.push(where + ": the stage is " + r.lay.reserved + "px tall, over 60% of a phone screen");
      if (capture) {
        const el = await p.$(`#${await p.evaluate((s) => window.__explainer.scenes[s].api.el.id || "", s)}`);
        const buf = el ? await el.screenshot() : await p.screenshot();
        shots.push({ label: r.name + " " + (i + 1) + "/" + n, b64: buf.toString("base64") });
      }
      steps++;
    }
    // Play the reader: click reader buttons and walk the steps they produce, measuring as before.
    if (clickSel && clickSel !== "none") {
      const r = await p.evaluate(async ([s, sel]) => {
        const { api } = window.__explainer.scenes[s];
        const out = [];
        const wait = () => new Promise((ok) => setTimeout(ok, 60));
        const live = () => [...api.el.querySelectorAll(sel)].find((b) => !b.disabled && b.offsetParent && getComputedStyle(b).visibility === "visible"
          && (!b.closest("[data-scene]") || b.closest("[data-scene]").classList.contains("on")));
        api.go(0); await wait();
        let clicks = 0;
        for (let k = 0; k < 80; k++) {
          const b = clicks < 8 ? live() : null;
          if (b) { clicks++; const label = b.textContent.trim().slice(0, 24); b.click(); await wait(); out.push({ at: "after clicking '" + label + "', step " + (api.index + 1), lay: window.__layoutOf(api), clicked: true }); continue; }
          if (api.index >= api.count - 1) break;
          api.next(); await wait();
          out.push({ at: "step " + (api.index + 1) + " of the reader's path", lay: window.__layoutOf(api) });
        }
        api.go(0);
        return out;
      }, [s, clickSel]);
      for (const x of r) track(tag, (await p.evaluate((s) => window.__explainer.scenes[s].name, s)), x.at, x.lay);
      if (r.some((x) => x.clicked)) clicked++;
    }
    await p.evaluate((s) => window.__explainer.scenes[s].api.go(0), s);
  }
  if (capture) pageChecks(await p.evaluate(() => window.__pageFacts()));
  const errs = await p.evaluate(() => window.__explainer.errors.slice());
  [...new Set(errs)].forEach((e) => problems.push(tag + "  player: " + e));
  await ctx.close();
  return steps;
}

const browser = await pw.chromium.launch();
const t0 = Date.now();
const steps = await walk(browser, 390, "light", true);
await walk(browser, 1100, "dark", false);

if (shots.length) {
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 800 }, deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  const cells = shots.map((s) => `<figure><img src="data:image/png;base64,${s.b64}"><figcaption>${s.label}</figcaption></figure>`).join("");
  await p.setContent(`<style>body{margin:0;padding:12px;background:#ddd;font:12px monospace;display:grid;grid-template-columns:repeat(auto-fill,300px);gap:12px;width:${Math.min(shots.length, 6) * 312 + 12}px}
    figure{margin:0;background:#fff;padding:4px}img{width:100%;display:block}figcaption{padding:4px 2px 0}</style>${cells}`);
  await p.waitForTimeout(100);
  await p.screenshot({ path: sheet, fullPage: true });
  await ctx.close();
}
await browser.close();

const uniq = [...new Set(problems)];
console.log((uniq.length ? "FAIL" : "PASS") + "  " + basename(page) + ": " + steps + " steps checked at 390px light and 1100px dark" + (clicked ? ", plus the reader's choices," : "") + " in " + ((Date.now() - t0) / 1000).toFixed(1) + "s");
uniq.slice(0, 20).forEach((p) => console.log("  - " + p));
if (uniq.length > 20) console.log("  ... and " + (uniq.length - 20) + " more");
[...new Set(notes)].slice(0, 8).forEach((n) => console.log("  note: " + n));
if (shots.length) console.log("  contact sheet: " + sheet);
process.exit(uniq.length ? 1 : 0);
