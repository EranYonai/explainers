#!/usr/bin/env python3
"""Assert every hex in each editor-scheme CSS exists in that scheme's primary-source palette.
Re-parses the cloned palette files under /tmp/schemes (see scheme_src.py) on every run."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scheme_src import SOURCES, hexes
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'themes')
bad = 0
for slug in SOURCES:
    src = hexes(slug)
    assert src, f'{slug}: no hex parsed from source files'
    css = open(os.path.join(D, slug + '.css'), encoding='utf-8').read()
    body = re.sub(r'/\*.*?\*/', '', css, flags=re.S)           # ignore the header comment
    used = {h.lower() for h in re.findall(r'#[0-9a-fA-F]{3,8}\b', body)}
    short = {h for h in used if len(h) != 7}
    missing = sorted(used - src)
    hdr = css.split('*/')[0]
    ok_hdr = all(k in hdr for k in ('Source: ' + SOURCES[slug]['url'], 'File: ', 'License: '))
    status = 'ok' if not missing and not short and ok_hdr else 'FAIL'
    print(f'{status:4} {slug:13} {len(used):2} hexes used, {len(src):3} in source' + (f'  missing={missing}' if missing else '') + ('' if ok_hdr else '  header incomplete'))
    bad += status != 'ok'
print('PASS' if not bad else f'FAIL ({bad})')
sys.exit(1 if bad else 0)
