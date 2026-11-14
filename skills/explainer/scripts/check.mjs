#!/usr/bin/env node
// Self-check for a built explainer page. One run, one short report, one contact sheet.
//
//   node check.mjs page.html [--sheet contact-sheet.png]
//
// Renders the page at phone width (390 px, light) and desktop width (1100 px, dark), walks every step of
// every scene, and reports:
//   - JS errors and console errors
//   - player errors: captions asking for a {value} that compute() does not provide, draw() failures
//   - sideways scroll on the page, and content wider than its scene, at any step
//   - captions longer than 200 characters (too long to read while something moves)
//   - external requests other than Google Fonts
// and writes a contact sheet: every step of every scene at phone width, in one image.
// Exit code: 0 pass, 1 fail, 3 skipped (Playwright not installed).
import { createRequire } from "node:module";
import { resolve, dirname, basename, join } from "node:path";
import { existsSync } from "node:fs";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const page = args.find((a) => !a.startsWith("--") && args[args.indexOf(a) - 1] !== "--sheet");
if (!page || !existsSync(page)) {
  console.error("usage: node check.mjs <page.html> [--sheet out.png]");
  process.exit(2);
}
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
        return { name, scroll: document.documentElement.scrollWidth - innerWidth, wide, len: text.length, scene: api.scene };
      }, [s, i]);
      const where = tag + "  " + r.name + " step " + (i + 1);
      if (r.scroll > 0) problems.push(where + ": page scrolls sideways by " + r.scroll + "px");
      if (r.wide) problems.push(where + ": content wider than the scene (" + r.wide + ")");
      if (r.len > 200) notes.push(where + ": caption is " + r.len + " characters; aim for under 200");
      if (capture) {
        const el = await p.$(`#${await p.evaluate((s) => window.__explainer.scenes[s].api.el.id || "", s)}`);
        const buf = el ? await el.screenshot() : await p.screenshot();
        shots.push({ label: r.name + " " + (i + 1) + "/" + n, b64: buf.toString("base64") });
      }
      steps++;
    }
    await p.evaluate((s) => window.__explainer.scenes[s].api.go(0), s);
  }
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
console.log((uniq.length ? "FAIL" : "PASS") + "  " + basename(page) + ": " + steps + " steps checked at 390px light and 1100px dark in " + ((Date.now() - t0) / 1000).toFixed(1) + "s");
uniq.slice(0, 20).forEach((p) => console.log("  - " + p));
if (uniq.length > 20) console.log("  ... and " + (uniq.length - 20) + " more");
[...new Set(notes)].slice(0, 8).forEach((n) => console.log("  note: " + n));
if (shots.length) console.log("  contact sheet: " + sheet);
process.exit(uniq.length ? 1 : 0);
