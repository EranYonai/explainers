#!/usr/bin/env node
// Build one self-contained explainer page from a source page.
//
//   node build.mjs page.src.html [-o page.html] [--theme inkwell]
//
// Without -o, page.src.html builds to page.html beside it. --theme builds with another theme than the page names.
//
// The source page references the shared pieces by placeholder, and this script inlines them:
//   <link rel="stylesheet" href="explainer:theme/inkwell">   -> Google Fonts link + theme tokens
//   <link rel="stylesheet" href="explainer:player.css">      -> player styles
//   <script src="explainer:player.js"></script>              -> player runtime
// No dependencies. The output has no external requests except Google Fonts.
import { readFileSync, writeFileSync, readdirSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const SKILL = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const THEMES = join(SKILL, "themes");
const TEMPLATES = join(SKILL, "templates");

function usage(msg) {
  if (msg) console.error(msg);
  console.error("usage: node build.mjs <page.src.html> [-o out.html] [--theme <name>]   themes: " + themes().join(", "));
  process.exit(2);
}
function themes() {
  return readdirSync(THEMES).filter((f) => f.endsWith(".css")).map((f) => f.slice(0, -4));
}

const args = process.argv.slice(2);
let src, out, themeOverride;
for (let i = 0; i < args.length; i++) {
  if (args[i] === "-o" || args[i] === "--theme") {
    const value = args[i + 1];
    if (!value || value.startsWith("-")) usage(args[i] + " needs a value");
    if (args[i] === "-o") out = value; else themeOverride = value;
    i++;
  }
  else if (args[i] === "-h" || args[i] === "--help") usage();
  else if (!src) src = args[i];
  else usage("unexpected argument: " + args[i]);
}
if (!src) usage();
if (!out && !src.endsWith(".src.html")) usage("the source does not end in .src.html, so say where the page goes with -o");
out = out || src.replace(/\.src\.html$/, ".html");

let html = readFileSync(src, "utf8");
const missing = [];

function themeBlock(name) {
  if (!themes().includes(name)) {
    missing.push("theme '" + name + "' (have: " + themes().join(", ") + ")");
    return "";
  }
  const css = readFileSync(join(THEMES, name + ".css"), "utf8");
  const fonts = (css.match(/Google Fonts:\s*(\S+)/) || [])[1];
  const links = fonts
    ? '<link rel="preconnect" href="https://fonts.googleapis.com">\n' +
      '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n' +
      '<link rel="stylesheet" href="' + fonts + '">\n'
    : "";
  return links + "<style>\n" + css.trim() + "\n</style>";
}

// A page needs all three pieces; a missing theme would still build and render with no colors or fonts.
for (const [name, re] of [["a theme link (href=\"explainer:theme/<name>\")", /href="explainer:theme\//],
  ["the player styles (href=\"explainer:player.css\")", /href="explainer:player\.css"/],
  ["the player script (src=\"explainer:player.js\")", /src="explainer:player\.js"/]]) {
  if (!re.test(html)) missing.push("the source is missing " + name);
}
html = html.replace(/<link[^>]*href="explainer:theme\/([\w-]+)"[^>]*>/g, (_, name) => themeBlock(themeOverride || name));
html = html.replace(/<link[^>]*href="explainer:player\.css"[^>]*>/g, () =>
  "<style>\n" + readFileSync(join(TEMPLATES, "player.css"), "utf8").trim() + "\n</style>");
html = html.replace(/<script[^>]*src="explainer:player\.js"[^>]*>\s*<\/script>/g, () =>
  "<script>\n" + readFileSync(join(TEMPLATES, "player.js"), "utf8").trim().replace(/<\/script/gi, "<\\/script") + "\n</script>");

// Only href and src values count, so prose that mentions a placeholder by name is fine.
const left = [...html.matchAll(/(?:href|src)="(explainer:[^"]*)"/g)].map((m) => m[1]);
if (left.length) missing.push("unresolved placeholders: " + [...new Set(left)].join(", "));
if (missing.length) {
  console.error("build failed:\n  " + missing.join("\n  "));
  process.exit(1);
}

mkdirSync(dirname(resolve(out)), { recursive: true });
writeFileSync(out, html);
const kb = (n) => (n / 1024).toFixed(1) + " KB";
console.log("built " + out + "  " + kb(Buffer.byteLength(html)) + "  (source " + kb(Buffer.byteLength(readFileSync(src))) + ")");
