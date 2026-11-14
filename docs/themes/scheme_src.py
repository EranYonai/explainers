"""Primary-source palette files for the editor color schemes. Shared by build.py and verify_schemes.py."""
import re, os
ROOT = '/tmp/schemes'
# slug -> dict(url, files (relative to ROOT), license, kind: 'hash' | 'nohash-json' | 'quoted' | 'lua')
SOURCES = {
 'rose-pine': dict(url='https://github.com/rose-pine/palette', files=['palette/palette.json'],
     license='MIT (palette/LICENSE, Copyright (c) mvllow)', kind='nohash'),
 'tokyo-night': dict(url='https://github.com/folke/tokyonight.nvim',
     files=['tokyonight.nvim/extras/lua/tokyonight_night.lua', 'tokyonight.nvim/extras/lua/tokyonight_day.lua'],
     license='Apache-2.0 (LICENSE)', kind='hash'),
 'dracula': dict(url='https://github.com/dracula/dracula-theme', files=['dracula-theme/README.md'],
     license='MIT (LICENSE, Copyright (c) 2023 Dracula Theme)', kind='hash'),
 'nord': dict(url='https://github.com/nordtheme/nord', files=['nord/src/nord.css'],
     license='MIT (license file, Copyright (c) 2016-present Sven Greb)', kind='hash'),
 'solarized': dict(url='https://github.com/altercation/solarized', files=['solarized/README.md'],
     license='MIT (LICENSE, Copyright (c) 2011 Ethan Schoonover)', kind='hash', linefilter=r'\$\w+:\s+#'),
 'oceanic-next': dict(url='https://github.com/voronianski/oceanic-next-color-scheme', files=['oceanic-next-color-scheme/README.md'],
     license='no LICENSE file in the repo; README states "MIT Licensed"', kind='hash'),
 'tomorrow': dict(url='https://github.com/chriskempson/tomorrow-theme',
     files=['tomorrow-theme/vim/colors/Tomorrow.vim', 'tomorrow-theme/vim/colors/Tomorrow-Night.vim'],
     license='MIT (LICENSE.md)', kind='quoted'),
 'iceberg': dict(url='https://github.com/cocopon/iceberg.vim', files=['iceberg.vim/colors/iceberg.vim'],
     license='MIT (LICENSE.txt, Copyright (c) 2014 cocopon)', kind='hash'),
 'one-half': dict(url='https://github.com/sonph/onehalf',
     files=['onehalf/vim/colors/onehalfdark.vim', 'onehalf/vim/colors/onehalflight.vim'],
     license='MIT (LICENSE.txt, Copyright (c) 2019 Son A. Pham)', kind='hash'),
 'kanagawa': dict(url='https://github.com/rebelot/kanagawa.nvim', files=['kanagawa.nvim/lua/kanagawa/colors.lua'],
     license='MIT (LICENSE, Copyright (c) 2021 Tommaso Laurenzi)', kind='lua'),
 'onedark': dict(url='https://github.com/navarasu/onedark.nvim', files=['onedark.nvim/lua/onedark/palette.lua'],
     license='MIT (LICENSE, Copyright (c) 2021 Navarasu)', kind='lua'),
 'gruvbox': dict(url='https://github.com/morhetz/gruvbox', files=['gruvbox/colors/gruvbox.vim'],
     license='no LICENSE file in the repo; package.json says "MIT" and README says "MIT/X11"', kind='hash'),
}
def hexes(slug):
    s = SOURCES[slug]; out = set()
    for f in s['files']:
        t = open(os.path.join(ROOT, f), encoding='utf-8').read()
        if s.get('linefilter'):
            t = '\n'.join(l for l in t.splitlines() if re.search(s['linefilter'], l))
        if s['kind'] == 'lua':
            t = re.sub(r'--[^\n]*', '', t)
        if s['kind'] == 'nohash':
            out |= {m.lower() for m in re.findall(r'"hex":\s*"([0-9a-fA-F]{6})"', t)}
        elif s['kind'] == 'quoted':
            out |= {m.lower() for m in re.findall(r'"([0-9a-fA-F]{6})"', t)}
        else:
            out |= {m.lower() for m in re.findall(r'#([0-9a-fA-F]{6})(?![0-9a-fA-F])', t)}
    return {'#' + h for h in out}
def files_text(slug):
    s = SOURCES[slug]
    return ', '.join(s['files'])
if __name__ == '__main__':
    for k in SOURCES: print(k, len(hexes(k)))
