# Checks

`scripts/check.mjs <page.html>` renders the page at 390 px (light) and 1100 px (dark) with reduced motion,
walks every step of every scene, and prints PASS or FAIL.

## What it catches

- JS errors and console errors.
- A caption asking for `{name}` that neither `compute()` nor the state provides (shown as `[?name]`).
- `draw()` or `setup()` throwing at any step.
- Sideways scroll on the page, and any element wider than its scene, at any step.
- Controls that move between steps, with the reason (stage, caption or controls row changed height). It also
  clicks the reader buttons (`--click "<selector>"`, default `.choices button`) and walks the steps they add,
  so a choice that grows the page is caught too. Pass your own selector when your buttons have other classes.
- A page or theme style overriding the stage or caption height the player reserves.
- Page parts (`data-slot`, see SKILL.md): missing `intro` (with `h1.hook` and `p.dek`), `scene` or `payoff`;
  parts out of order; an unknown `data-slot` name; more than one `h1`; a `.cite` link pointing at no source; a
  source without a link.
- A page built without a theme.
- In the page's own code: a literal color in its styles (hex, `rgb()`, `hsl()`), `Math.random`, and
  `api.branch` without a `branches` list.
- Requests to anything other than Google Fonts.
- Notes, not failures: captions over 200 characters, a stage taller than 60% of a phone screen, more than
  400 words outside the scene, outside links with no Sources part, and a step that waits for the reader
  when no button matched the click selector (so the reader's path was not checked).

It writes a contact sheet (`<page>.sheet.png`): every step at phone width in one image. Look at it once.

## What you must eyeball on the contact sheet

- Labels overlapping or clipped, especially at the ends of a row and on the phone.
- A caption that contradicts the picture ("three wait" while two are drawn).
- A short section in a tall stage: lots of empty space on a phone. Move content between sections to even them out.
- A step where nothing visibly changes.
- Color carrying meaning alone: good and bad also need a glyph or a word.

## What no script catches

- Facts. For current tools and libraries, check the claim against the primary source and cite it.
- Numbers typed into prose outside captions. Search the page for digits and make sure each comes from code.
- The reader action not mattering: try two different choices and confirm the outcome differs.
- Confidential details: internal names, hosts, customers, ticket ids.
