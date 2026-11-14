#!/usr/bin/env node
// Repo tooling (not part of the skill): build or check every example and starter.
//
//   node scripts/all.mjs build    examples/*/page.src.html -> examples/*/index.html, starters -> out/starters/
//   node scripts/all.mjs check    build, then run the skill's check on every page (needs Playwright)
//
// CI runs `check` and then fails if the committed example pages differ from a fresh build.
import { readdirSync, existsSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SKILL = join(ROOT, "skills", "explainer");
const BUILD = join(SKILL, "scripts", "build.mjs");
const CHECK = join(SKILL, "scripts", "check.mjs");
const OUT = join(ROOT, "out");

const pages = [];
for (const d of readdirSync(join(ROOT, "examples")).sort()) {
  const src = join(ROOT, "examples", d, "page.src.html");
  if (existsSync(src)) pages.push({ name: "examples/" + d, src, out: join(ROOT, "examples", d, "index.html") });
}
const kinds = join(SKILL, "starters");
for (const f of readdirSync(kinds).filter((f) => f.endsWith(".src.html")).sort()) {
  pages.push({ name: "starter " + f, src: join(kinds, f), out: join(OUT, "starters", f.replace(".src.html", ".html")) });
}

function run(script, args) {
  const r = spawnSync(process.execPath, [script, ...args], { encoding: "utf8" });
  return { ok: r.status === 0, code: r.status, text: (r.stdout + r.stderr).trim() };
}

const cmd = process.argv[2];
if (cmd !== "build" && cmd !== "check") {
  console.error("usage: node scripts/all.mjs build|check");
  process.exit(2);
}

let failed = 0;
for (const p of pages) {
  const b = run(BUILD, [p.src, "-o", p.out]);
  if (!b.ok) { failed++; console.log("FAIL  build " + p.name + "\n" + b.text); continue; }
  if (cmd === "build") { console.log(b.text.replace(ROOT + "/", "")); continue; }
  const c = run(CHECK, [p.out, "--sheet", join(OUT, "sheets", p.name.replace(/[^\w.-]+/g, "_") + ".png")]);
  if (c.code === 3) { console.log(c.text); process.exit(3); }
  if (!c.ok) failed++;
  console.log(p.name + "\n  " + c.text.split("\n").filter((l) => !l.includes("contact sheet:")).join("\n  "));
}
console.log((failed ? "FAIL" : "PASS") + "  " + (pages.length - failed) + " of " + pages.length + " pages " + (cmd === "build" ? "built" : "passed"));
process.exit(failed ? 1 : 0);
