# Theme gallery

`index.html` shows all 25 themes. `themes/*.css` are drop-in token files. The skill ships
eight (`skills/explainer/themes/`): Inkwell, plus Flight Deck and Transit (taken from two drafts, not in this
gallery), plus five editor palettes: Gruvbox, Kanagawa, One Half, Dracula and Rose Pine. The rest live here as
the pool new ones come from.

- `build.py` generates `index.html` and `themes/*.css`. Edit it and rerun `python3 build.py`. Do not hand-edit the outputs.
- `verify_schemes.py` checks the 12 editor schemes against their upstream palettes. It expects those repos cloned
  under `/tmp/schemes` (paths in `scheme_src.py`).
- `shot.py` renders the gallery at phone and desktop width with Playwright.

Required tokens: `--paper --surface --ink --muted --line --accent --hl --good --bad --font-display --font-body --font-mono`.
