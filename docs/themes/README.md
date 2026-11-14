# Theme gallery

`index.html` shows all 25 themes. `themes/*.css` are drop-in token files. Only three ship with the skill
(`skills/explainer/themes/`: Inkwell, Whiteprint, Two-Ink); the rest live here as the pool new ones come from.

- `build.py` generates `index.html` and `themes/*.css`. Edit it and rerun `python3 build.py`. Do not hand-edit the outputs.
- `verify_schemes.py` checks the 12 editor schemes against their upstream palettes. It expects those repos cloned
  under `/tmp/schemes` (paths in `scheme_src.py`).
- `shot.py` renders the gallery at phone and desktop width with Playwright.

Required tokens: `--paper --surface --ink --muted --line --accent --hl --good --bad --font-display --font-body --font-mono`.
