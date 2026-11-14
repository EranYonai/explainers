# Checks

`scripts/check.mjs <page.html>` renders the page at 390 px (light) and 1100 px (dark) with reduced motion,
walks every step of every scene, and prints PASS or FAIL.

## What it catches

- JS errors and console errors.
- A caption asking for `{name}` that neither `compute()` nor the state provides (shown as `[?name]`).
- `draw()` or `setup()` throwing at any step.
- Sideways scroll on the page, and any element wider than its scene, at any step.
- Requests to anything other than Google Fonts.
- Captions over 200 characters (a note, not a failure).

It writes a contact sheet (`<page>.sheet.png`): every step at phone width in one image. Look at it once.

## What you must eyeball on the contact sheet

- Labels overlapping or clipped, especially at the ends of a row and on the phone.
- A caption that contradicts the picture ("three wait" while two are drawn).
- Height jumps between steps that would make the controls move under the reader's thumb.
- A step where nothing visibly changes.
- Color carrying meaning alone: good and bad also need a glyph or a word.

## What no script catches

- Facts. For current tools and libraries, check the claim against the primary source and cite it.
- Numbers typed into prose outside captions. Search the page for digits and make sure each comes from code.
- The reader action not mattering: try two different choices and confirm the outcome differs.
- Confidential details: internal names, hosts, customers, ticket ids.
