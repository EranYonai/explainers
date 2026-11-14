import json, html, os
from scheme_src import SOURCES, files_text
OUT=os.path.dirname(os.path.abspath(__file__))
def T(slug,name,mood,best,risk,hand,fonts,gf,light,dark,style,single=None,src=None):
    return dict(slug=slug,name=name,mood=mood,best=best,risk=risk,hand=hand,fonts=fonts,gf=gf,light=light,dark=dark,style=style,single=single,src=src)
def C(paper,surface,ink,muted,line,accent,hl,good,bad,accent_ink,extra=None):
    d={'--paper':paper,'--surface':surface,'--ink':ink,'--muted':muted,'--line':line,'--accent':accent,'--hl':hl,'--good':good,'--bad':bad,'--accent-ink':accent_ink,'--hl-ink':'#111111'}
    if extra: d.update(extra)
    return d
MONO_FB='ui-monospace,Menlo,Consolas,monospace'
themes=[
T('inkwell','Inkwell','A ruled notebook, a black fineliner and one green highlighter.',
  'Step-by-step reasoning, debugging stories, anything Eran would sketch by hand.',
  'Handwritten titles get hard to read when they run long. Keep them under six words.',4,
  'Caveat / Newsreader / IBM Plex Mono','Caveat:wght@600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=IBM+Plex+Mono:wght@400;600',
  C('#f1f1ee','#fbfbf9','#1d1d22','#55565f','#c4cbd8','#1456b8','#c8f03c','#1d7a45','#c8322b','#ffffff',
    {'--texture':'repeating-linear-gradient(to bottom,transparent 0 25px,color-mix(in srgb,var(--accent) 22%,transparent) 25px 26px)','--shadow':'0 1px 0 rgba(0,0,0,.08)'}),
  C('#161618','#1f1f23','#ecebe6','#a5a49c','#3a3a40','#7fb2ff','#c8f03c','#5fd38a','#ff7b6e','#101014',
    {'--texture':'repeating-linear-gradient(to bottom,transparent 0 25px,color-mix(in srgb,var(--accent) 16%,transparent) 25px 26px)','--shadow':'none'}),
  {'--font-display':'"Caveat","Segoe Print",cursive','--font-body':'"Newsreader",Georgia,serif','--font-mono':'"IBM Plex Mono",'+MONO_FB,
   '--radius':'3px','--stroke-width':'2','--sketch':'2.4','--display-scale':'1.45','--display-weight':'700','--display-transform':'none','--display-tracking':'0','--border-width':'1px','--linecap':'round','--node-rx':'13px'}),
T('whiteprint','Whiteprint','An engineering drawing. Thin exact lines on a measured grid.',
  'Architecture, memory layouts, protocols, low-level and systems topics.',
  'Everything is blue, so good and bad lean on glyphs and labels more than on color.',0,
  'Barlow Condensed / Barlow / Share Tech Mono','Barlow+Condensed:wght@500;600&family=Barlow:ital,wght@0,400;0,600;1,400&family=Share+Tech+Mono',
  C('#eaf1f8','#f6f9fc','#0f3a78','#44648f','#a9c0de','#0b55c8','#ff8a1f','#0a7a5a','#c62a3a','#ffffff',
    {'--texture':'linear-gradient(color-mix(in srgb,var(--line) 45%,transparent) 1px,transparent 1px),linear-gradient(90deg,color-mix(in srgb,var(--line) 45%,transparent) 1px,transparent 1px)','--texture-size':'20px 20px'}),
  C('#0d3b78','#114487','#eaf3ff','#b9cff0','#3f6cab','#a8d4ff','#ffc14d','#7ff0c0','#ffaaa8','#0a2c5c',
    {'--texture':'linear-gradient(color-mix(in srgb,var(--line) 45%,transparent) 1px,transparent 1px),linear-gradient(90deg,color-mix(in srgb,var(--line) 45%,transparent) 1px,transparent 1px)','--texture-size':'20px 20px'}),
  {'--font-display':'"Barlow Condensed","Arial Narrow",sans-serif','--font-body':'"Barlow","Helvetica Neue",sans-serif','--font-mono':'"Share Tech Mono",'+MONO_FB,
   '--radius':'0px','--stroke-width':'1.25','--sketch':'0','--shadow':'none','--display-scale':'1.15','--display-weight':'600','--display-transform':'uppercase','--display-tracking':'.06em','--border-width':'1px','--linecap':'butt','--node-rx':'0px'}),
T('dry-erase','Dry Erase','A whiteboard after a good design review. Fat markers, four colors.',
  'Agent loops, pipelines, informal walk-throughs for a team.',
  'Closest to the common Excalidraw look. Least distinctive of the hand-drawn set.',3,
  'Gochi Hand / Figtree / Fira Code','Gochi+Hand&family=Figtree:ital,wght@0,400;0,600;1,400&family=Fira+Code:wght@400;600',
  C('#f4f6f7','#ffffff','#16181d','#5b616e','#d0d5dd','#0a63d8','#ff9a1f','#0f8a3c','#d92626','#ffffff',{'--shadow':'0 2px 10px rgba(20,30,50,.10)'}),
  C('#1b1f24','#242a31','#f2f4f6','#a6aebb','#3d4550','#5cb0ff','#ffb347','#5ad67d','#ff6b6b','#0e1114',{'--shadow':'0 2px 10px rgba(0,0,0,.35)'}),
  {'--font-display':'"Gochi Hand","Comic Sans MS",cursive','--font-body':'"Figtree","Segoe UI",sans-serif','--font-mono':'"Fira Code",'+MONO_FB,
   '--radius':'14px','--stroke-width':'3.4','--sketch':'1.6','--texture':'none','--display-scale':'1.25','--display-weight':'400','--display-transform':'none','--display-tracking':'0','--border-width':'2px','--linecap':'round','--node-rx':'13px'}),
T('phosphor','Phosphor','A green CRT at 2 a.m. Everything is a character cell.',
  'Shells, CI logs, kernels, bytes and bits. Engineers who live in a terminal.',
  'Long prose in mono green is tiring. Keep paragraphs to two or three lines.',0,
  'VT323 / JetBrains Mono / JetBrains Mono','VT323&family=JetBrains+Mono:ital,wght@0,400;0,700;1,400',
  C('#07100a','#0c1a10','#8bf7a3','#58b672','#1f4d2d','#c4ffd3','#ffb000','#4dff88','#ff6a60','#07100a',
    {'--texture':'repeating-linear-gradient(to bottom,transparent 0 2px,rgba(0,0,0,.28) 2px 3px)','--shadow':'0 0 18px rgba(77,255,136,.12)'}),
  None,
  {'--font-display':'"VT323","Courier New",monospace','--font-body':'"JetBrains Mono",'+MONO_FB,'--font-mono':'"JetBrains Mono",'+MONO_FB,
   '--radius':'0px','--stroke-width':'2','--sketch':'0','--display-scale':'1.5','--display-weight':'400','--display-transform':'uppercase','--display-tracking':'.03em','--border-width':'1px','--linecap':'butt','--node-rx':'0px','--body-scale':'.9'},
  single='Dark only. The glow is the identity.'),
T('raster','Raster','Swiss poster discipline. Black rules, one heavy grotesque, lots of air.',
  'Concepts and comparisons, conference-grade explainers, senior audiences.',
  'Can feel cold and corporate. The least personal of the ten.',0,
  'Archivo / Archivo / DM Mono','Archivo:ital,wght@0,400;0,600;0,900;1,400&family=DM+Mono:wght@400;500',
  C('#ffffff','#f2f2f2','#0a0a0a','#595959','#0a0a0a','#1433d6','#ffd400','#00804a','#d4001a','#ffffff'),
  C('#0b0b0b','#191919','#f5f5f5','#a8a8a8','#f5f5f5','#8ea2ff','#ffd400','#35d68a','#ff5a5f','#0b0b0b'),
  {'--font-display':'"Archivo","Helvetica Neue",Arial,sans-serif','--font-body':'"Archivo","Helvetica Neue",Arial,sans-serif','--font-mono':'"DM Mono",'+MONO_FB,
   '--radius':'0px','--stroke-width':'2.5','--sketch':'0','--shadow':'none','--texture':'none','--display-scale':'1.2','--display-weight':'900','--display-transform':'none','--display-tracking':'-.025em','--border-width':'3px','--linecap':'butt','--node-rx':'13px'}),
T('two-ink','Two-Ink','A risograph zine. Navy and hot pink, slightly off register.',
  'Opinionated essays, reels, short punchy explainers that get shared.',
  'The pink highlight sits near the red of bad. Keep the cross glyph on bad states.',2,
  'Dela Gothic One / Space Grotesk / Space Mono','Dela+Gothic+One&family=Space+Grotesk:wght@400;600&family=Space+Mono:ital,wght@0,400;0,700;1,400',
  C('#f1ece1','#f9f5ec','#1b1f4b','#4f5488','#b9bde0','#2438cf','#ff6fa8','#00795c','#b3261e','#ffffff',
    {'--texture':'radial-gradient(color-mix(in srgb,var(--hl) 24%,transparent) 1.2px,transparent 1.4px)','--texture-size':'9px 9px','--shadow':'5px 5px 0 var(--hl)'}),
  C('#15163a','#1d1f4d','#f3efe4','#b7b8da','#3e4180','#9db8ff','#ff6fa8','#49d6b0','#ff8a6b','#15163a',
    {'--texture':'radial-gradient(color-mix(in srgb,var(--hl) 22%,transparent) 1.2px,transparent 1.4px)','--texture-size':'9px 9px','--shadow':'5px 5px 0 var(--hl)'}),
  {'--font-display':'"Dela Gothic One","Arial Black",sans-serif','--font-body':'"Space Grotesk","Trebuchet MS",sans-serif','--font-mono':'"Space Mono",'+MONO_FB,
   '--radius':'2px','--stroke-width':'3','--sketch':'1','--display-scale':'1.05','--display-weight':'400','--display-transform':'none','--display-tracking':'-.01em','--border-width':'2px','--linecap':'square','--node-rx':'5px'}),
T('slate','Slate','A classroom board. Dusty chalk, four sticks of color.',
  'Fundamentals, algorithms, first-principles lessons for newcomers.',
  'Reads as school. Senior engineers may find it cute rather than serious.',5,
  'Cabin Sketch / Patrick Hand / Cutive Mono','Cabin+Sketch:wght@400;700&family=Patrick+Hand&family=Cutive+Mono',
  C('#23302b','#2a3832','#f1efe6','#bcc4b9','#56675f','#a9dcff','#ffe27a','#a5e8a0','#ffa39a','#1a2420',
    {'--texture':'radial-gradient(ellipse at 20% 10%,rgba(255,255,255,.06),transparent 55%),radial-gradient(ellipse at 85% 90%,rgba(255,255,255,.05),transparent 50%)','--shadow':'none'}),
  None,
  {'--font-display':'"Cabin Sketch","Chalkduster",cursive','--font-body':'"Patrick Hand","Comic Sans MS",cursive','--font-mono':'"Cutive Mono",'+MONO_FB,
   '--radius':'4px','--stroke-width':'3','--sketch':'3.2','--display-scale':'1.2','--display-weight':'700','--display-transform':'none','--display-tracking':'.01em','--border-width':'2px','--linecap':'round','--node-rx':'13px','--body-scale':'1.1'},
  single='Dark only. A white chalkboard is a whiteboard.'),
T('placard','Placard','A museum wall label. Quiet, exact, a little ceremonial.',
  'History of an idea, deep dives, reference pieces people return to.',
  'Hairline strokes thin out on a phone and in reels. Diagrams need generous size.',0,
  'Marcellus / Spectral / Courier Prime','Marcellus&family=Spectral:ital,wght@0,400;0,600;1,400&family=Courier+Prime:wght@400;700',
  C('#e9e8e4','#f7f6f3','#22252a','#595d64','#c6c4bd','#2b4a7a','#c79a2b','#2e6e45','#a8322d','#ffffff',{'--shadow':'0 10px 24px -14px rgba(0,0,0,.35)'}),
  C('#1c1d20','#26282c','#e9e6df','#a9a69e','#43464c','#9db8e6','#d9b45a','#7fc494','#e88a80','#16171a',{'--shadow':'0 10px 24px -14px rgba(0,0,0,.8)'}),
  {'--font-display':'"Marcellus","Trajan Pro",serif','--font-body':'"Spectral",Georgia,serif','--font-mono':'"Courier Prime","Courier New",monospace',
   '--radius':'2px','--stroke-width':'1.4','--sketch':'0','--texture':'none','--display-scale':'1.1','--display-weight':'400','--display-transform':'uppercase','--display-tracking':'.09em','--border-width':'1px','--linecap':'butt','--node-rx':'13px'}),
T('panel','Panel','A comic page. Thick outlines, flat primaries, hard shadows.',
  'Stories with a villain: flaky tests, race conditions, incident retros.',
  'Loud. It can undercut serious material and tires over a long explainer.',3,
  'Bangers / Comic Neue / Ubuntu Mono','Bangers&family=Comic+Neue:ital,wght@0,400;0,700;1,400&family=Ubuntu+Mono:wght@400;700',
  C('#eef4ff','#ffffff','#111111','#4a4a4a','#111111','#1a5fe0','#ffd60a','#128a3e','#e02020','#ffffff',
    {'--texture':'radial-gradient(color-mix(in srgb,var(--accent) 18%,transparent) 1.5px,transparent 1.7px)','--texture-size':'10px 10px','--shadow':'5px 5px 0 var(--ink)'}),
  C('#14141c','#1f1f2b','#ffffff','#b9b9c6','#ffffff','#7fb0ff','#ffd60a','#4fe07f','#ff6464','#14141c',
    {'--texture':'radial-gradient(color-mix(in srgb,var(--accent) 22%,transparent) 1.5px,transparent 1.7px)','--texture-size':'10px 10px','--shadow':'5px 5px 0 var(--hl)'}),
  {'--font-display':'"Bangers","Impact",sans-serif','--font-body':'"Comic Neue","Comic Sans MS",sans-serif','--font-mono':'"Ubuntu Mono",'+MONO_FB,
   '--radius':'0px','--stroke-width':'3.6','--sketch':'0.8','--display-scale':'1.4','--display-weight':'400','--display-transform':'uppercase','--display-tracking':'.04em','--border-width':'3px','--linecap':'round','--node-rx':'13px','--body-scale':'1.05'}),
T('tm-9','TM-9','A service manual. Numbered figures, stamp blue, safety orange.',
  'Runbooks, CI gate guides, procedures, how-to for on-call engineers.',
  'Dry by design. It teaches procedure well and wonder badly.',0,
  'Big Shoulders Display / Public Sans / Red Hat Mono','Big+Shoulders+Display:wght@700;800&family=Public+Sans:ital,wght@0,400;0,600;1,400&family=Red+Hat+Mono:wght@400;600',
  C('#e9e9e1','#f6f6f0','#1e2a22','#535c4e','#a9ad9c','#24406e','#ff7a00','#2f7d32','#b3202a','#ffffff'),
  C('#1a1e1a','#232823','#e6e6da','#a5aa98','#474e43','#9fbce8','#ff8f1f','#7fcf7a','#ff7d78','#141714'),
  {'--font-display':'"Big Shoulders Display","Oswald","Arial Narrow",sans-serif','--font-body':'"Public Sans","Segoe UI",sans-serif','--font-mono':'"Red Hat Mono",'+MONO_FB,
   '--radius':'1px','--stroke-width':'2','--sketch':'0','--shadow':'none','--texture':'none','--display-scale':'1.3','--display-weight':'800','--display-transform':'uppercase','--display-tracking':'.03em','--border-width':'2px','--linecap':'butt','--node-rx':'3px'}),
T('catppuccin','Catppuccin','Soft pastels from the editor theme many developers already run. Latte by day, Mocha by night.',
  'Developer tooling, agents, editors and terminals. Readers who already use Catppuccin will feel at home.',
  'It is a popular palette, so it reads as "dev setup" more than as your own look. In Latte, green is too faint, so "good" uses teal, and text on the yellow highlight is only 3:1, so keep it bold.',1,
  'Fredoka / Nunito / JetBrains Mono','Fredoka:wght@500;600&family=Nunito:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:ital,wght@0,400;0,700;1,400',
  C('#e6e9ef','#eff1f5','#4c4f69','#5c5f77','#bcc0cc','#8839ef','#df8e1d','#179299','#d20f39','#eff1f5',{'--hl-ink':'#4c4f69','--shadow':'0 2px 12px rgba(76,79,105,.10)'}),
  C('#1e1e2e','#313244','#cdd6f4','#a6adc8','#45475a','#cba6f7','#f9e2af','#a6e3a1','#f38ba8','#11111b',{'--hl-ink':'#11111b','--shadow':'0 2px 14px rgba(0,0,0,.35)'}),
  {'--font-display':'"Fredoka","Nunito","Segoe UI",sans-serif','--font-body':'"Nunito","Segoe UI",sans-serif','--font-mono':'"JetBrains Mono",'+MONO_FB,'--radius':'14px','--stroke-width':'2.6','--sketch':'0','--texture':'none','--display-scale':'1.2','--display-weight':'600','--display-transform':'none','--display-tracking':'-.01em','--border-width':'1.5px','--linecap':'round','--node-rx':'13px'}),
T('catppuccin-frappe','Catppuccin Frappé','The softest dark flavor. Muted, low glare, easy on long reads.',
  'Long-form explainers read at night, slower conceptual pieces.',
  'The lowest contrast of the dark flavors. Thin strokes fade on a phone in sunlight.',1,
  'Fredoka / Nunito / JetBrains Mono','Fredoka:wght@500;600&family=Nunito:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:ital,wght@0,400;0,700;1,400',
  C('#303446','#292c3c','#c6d0f5','#a5adce','#51576d','#ca9ee6','#e5c890','#a6d189','#e78284','#232634',{'--hl-ink':'#232634','--shadow':'0 2px 14px rgba(0,0,0,.30)'}),
  None,{'--font-display':'"Fredoka","Nunito","Segoe UI",sans-serif','--font-body':'"Nunito","Segoe UI",sans-serif','--font-mono':'"JetBrains Mono",'+MONO_FB,'--radius':'14px','--stroke-width':'2.6','--sketch':'0','--texture':'none','--display-scale':'1.2','--display-weight':'600','--display-transform':'none','--display-tracking':'-.01em','--border-width':'1.5px','--linecap':'round','--node-rx':'13px'},single='Dark only. Frappé is a dark flavor; use Catppuccin for Latte in light mode.'),
T('catppuccin-macchiato','Catppuccin Macchiato','Between Frappé and Mocha. Deeper navy, a little more pop.',
  'Agent and AI topics, demos shown on a big screen.',
  'Close to Mocha. Pick one dark flavor as a house default rather than mixing them.',1,
  'Fredoka / Nunito / JetBrains Mono','Fredoka:wght@500;600&family=Nunito:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:ital,wght@0,400;0,700;1,400',
  C('#24273a','#363a4f','#cad3f5','#a5adcb','#494d64','#c6a0f6','#eed49f','#a6da95','#ed8796','#181926',{'--hl-ink':'#181926','--shadow':'0 2px 14px rgba(0,0,0,.35)'}),
  None,{'--font-display':'"Fredoka","Nunito","Segoe UI",sans-serif','--font-body':'"Nunito","Segoe UI",sans-serif','--font-mono':'"JetBrains Mono",'+MONO_FB,'--radius':'14px','--stroke-width':'2.6','--sketch':'0','--texture':'none','--display-scale':'1.2','--display-weight':'600','--display-transform':'none','--display-tracking':'-.01em','--border-width':'1.5px','--linecap':'round','--node-rx':'13px'},single='Dark only. Macchiato is a dark flavor; use Catppuccin for Latte in light mode.'),
]
# ---- editor color schemes (colors from each scheme's primary source, see scheme_src.py)
ED_STYLE={'--font-display':'"Space Grotesk","Segoe UI",sans-serif','--font-body':'"Figtree","Segoe UI",sans-serif','--font-mono':'"JetBrains Mono",'+MONO_FB,'--radius':'6px','--stroke-width':'2.4','--sketch':'0','--texture':'none','--display-scale':'1.1','--display-weight':'600','--display-transform':'none','--display-tracking':'-.01em','--border-width':'1.5px','--linecap':'round','--node-rx':'6px'}
ED_FONTS='Space Grotesk / Figtree / JetBrains Mono'
ED_GF='Space+Grotesk:wght@400;600&family=Figtree:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:ital,wght@0,400;0,700;1,400'
def ED(slug,name,src,mood,best,risk,light,dark,single=None,style=None,fonts=None,gf=None):
    return T(slug,name,mood,best,risk,1,fonts or ED_FONTS,gf or ED_GF,light,dark,style or ED_STYLE,single=single,src=src)
def H(ink): return {'--hl-ink':ink}
themes+=[
ED('rose-pine','Rosé Pine','rose-pine',
  'Soft rose and iris on deep plum. Dawn by day, the main dark by night.',
  'Calm, design-minded explainers about tools and craft. Readers who like a quiet, warm editor theme.',
  'Rosé Pine has no green, so "good" uses foam teal. The Moon variant is not included. Muted text uses the main variant gray because the Dawn subtle tone is too faint.',
  C('#faf4ed','#fffaf3','#464261','#6e6a86','#f2e9e1','#286983','#ea9d34','#56949f','#b4637a','#faf4ed',H('#191724')),
  C('#191724','#1f1d2e','#e0def4','#908caa','#26233a','#ebbcba','#f6c177','#9ccfd8','#eb6f92','#191724',H('#191724'))),
ED('tokyo-night','Tokyo Night','tokyo-night',
  'Cool indigo with neon blue. Night by night, Day for the light toggle.',
  'Agent and AI topics, demos on a big screen, anything with a late-night terminal feel.',
  'Very popular, so it reads as a dev setup. Storm is not included. Day is a cool blue-gray, and its signature blue is too faint, so the accent is purple.',
  C('#e1e2e7','#e1e2e7','#3760bf','#006a83','#b4b5b9','#7847bd','#b15c00','#587539','#c64343','#e1e2e7',H('#ffffff')),
  C('#1a1b26','#292e42','#c0caf5','#a9b1d6','#3b4261','#7aa2f7','#e0af68','#9ece6a','#f7768e','#1a1b26',H('#1a1b26'))),
ED('dracula','Dracula','dracula',
  'Vivid pink and purple on a dark slate. Alucard is the light twin.',
  'Punchy, high-energy explainers and reels. Readers who already run Dracula everywhere.',
  'Dracula defines one background, so paper and surface share it. Muted text uses purple because the official comment blue is too faint.',
  C('#fffbeb','#fffbeb','#1f1f1f','#6c664b','#cfcfde','#644ac9','#a34d14','#14710a','#cb3a2a','#fffbeb',H('#fffbeb')),
  C('#282a36','#282a36','#f8f8f2','#bd93f9','#44475a','#ff79c6','#ffb86c','#50fa7b','#ff5555','#282a36',H('#282a36'))),
ED('nord','Nord','nord',
  'Arctic blue-gray with frost accents. Calm, cool and low glare.',
  'Long reads and technical docs. Anything that should feel quiet and tidy.',
  'Dark only. Nord has one background shade here, so paper and surface match. Muted text is blue-gray, so keep long passages in the main ink.',
  C('#2e3440','#2e3440','#d8dee9','#81a1c1','#434c5e','#88c0d0','#ebcb8b','#a3be8c','#bf616a','#2e3440',H('#2e3440')),
  None,single='Dark only. Nord defines only a dark palette; the toggle does not change it.'),
ED('solarized','Solarized','solarized',
  'Warm paper and teal-blue ink, tuned for low eye strain. Light and dark share one set.',
  'Long reading sessions and print-like pages. Readers who know Solarized from their terminal.',
  'Its contrast is low by design. Paper and surface match. In light mode the accent is 4.3:1 and green is 3:1, so keep them bold.',
  C('#fdf6e3','#fdf6e3','#073642','#586e75','#eee8d5','#cb4b16','#b58900','#859900','#dc322f','#fdf6e3',H('#002b36')),
  C('#002b36','#002b36','#eee8d5','#93a1a1','#073642','#2aa198','#b58900','#859900','#dc322f','#002b36',H('#002b36'))),
ED('oceanic-next','Oceanic Next','oceanic-next',
  'Deep sea slate with a soft blue accent. A calm base16 dark.',
  'Tooling and infrastructure topics. A steady, low-drama dark look.',
  'Dark only. The repo has no light variant. The accent is teal because the signature blue is too faint on the surface.',
  C('#1b2b34','#343d46','#d8dee9','#a7adba','#4f5b66','#5fb3b3','#fac863','#99c794','#ec5f67','#1b2b34',H('#1b2b34')),
  None,single='Dark only. The Oceanic Next repo defines only a dark palette.'),
ED('tomorrow','Tomorrow','tomorrow',
  'Plain white with muted primaries. Tomorrow Night for the dark side.',
  'Clean, neutral explainers. The safest pick if you want a theme nobody argues about.',
  'Light and Night come from the same author but different files. Paper and surface are both white.',
  C('#ffffff','#ffffff','#4d4d4c','#666666','#d6d6d6','#4271ae','#eab700','#718c00','#c82829','#ffffff',H('#4d4d4c')),
  C('#1d1f21','#282a2e','#c5c8c6','#969896','#373b41','#81a2be','#f0c674','#b5bd68','#cc6666','#1d1f21',H('#1d1f21'))),
ED('iceberg','Iceberg','iceberg',
  'Cool blue-gray with soft pastels. Easy on the eyes in both modes.',
  'Dense diagrams and code-heavy steps where you want little color noise.',
  'The palette is muted, so status colors are close in hue. Do not rely on color alone for good and bad.',
  C('#dcdfe7','#e8e9ec','#33374c','#505695','#c9cdd7','#2d539e','#eac6ad','#668e3d','#cc517a','#e8e9ec',H('#33374c')),
  C('#161821','#1e2132','#c6c8d1','#8389a3','#2a3158','#84a0c6','#e2a478','#b4be82','#e27878','#161821',H('#161821'))),
ED('one-half','One Half','one-half',
  'Atom-style gray with bright, friendly accents. Light and dark pair.',
  'General dev explainers. A familiar look for readers coming from Atom or VS Code One Dark.',
  'The light version has no readable mid gray, so muted text is blue at 3.7:1 and the accent is purple. In dark mode paper and surface match.',
  C('#f0f0f0','#fafafa','#383a42','#0184bc','#d4d4d4','#a626a4','#bfceff','#50a14f','#e45649','#fafafa',H('#383a42')),
  C('#282c34','#282c34','#dcdfe4','#919baa','#474e5d','#61afef','#e5c07b','#98c379','#e06c75','#282c34',H('#282c34'))),
ED('kanagawa','Kanagawa','kanagawa',
  'Ink and paper after Hokusai. Wave by night, Lotus by day.',
  'Story-driven explainers with a craft feel. Works well with the serif fonts.',
  'Lotus is a warm yellow paper, not white. Wave accents are soft, so thin lines need the heavier stroke.',
  C('#e5ddb0','#f2ecbc','#43436c','#545464','#d5cea3','#5d57a3','#f9d791','#6f894e','#c84053','#f2ecbc',H('#43436c')),
  C('#1f1f28','#2a2a37','#dcd7ba','#c8c093','#363646','#7e9cd8','#e6c384','#98bb6c','#e46876','#1f1f28',H('#1f1f28')),
  style=dict(ED_STYLE,**{'--font-display':'"Marcellus","Trajan Pro",serif','--font-body':'"Spectral",Georgia,serif','--display-weight':'400','--display-scale':'1.2'}),
  fonts='Marcellus / Spectral / JetBrains Mono',
  gf='Marcellus&family=Spectral:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:ital,wght@0,400;0,700;1,400'),
ED('onedark','OneDark','onedark',
  'The classic Atom dark with blue, green and yellow. A light style exists too.',
  'Mainstream developer topics. The most familiar editor look for many readers.',
  'It is everywhere, so it adds no personality. Muted gray is faint in both styles, around 3.3 to 4.1:1.',
  C('#f0f0f0','#fafafa','#383a42','#818387','#dcdcdc','#a626a4','#986801','#50a14f','#e45649','#fafafa',H('#fafafa')),
  C('#282c34','#282c34','#abb2bf','#848b98','#3b3f4c','#61afef','#e5c07b','#98c379','#e86671','#21252b',H('#21252b'))),
ED('gruvbox','Gruvbox','gruvbox',
  'Warm retro cream and brown with orange accents. Dark and light.',
  'Terminal and Unix topics. A cozy, retro look that suits shell sessions.',
  'The warm browns can look muddy on cheap screens. Orange and green are close in lightness.',
  C('#f2e5bc','#fbf1c7','#3c3836','#665c54','#d5c4a1','#af3a03','#d79921','#79740e','#9d0006','#fbf1c7',H('#282828')),
  C('#282828','#3c3836','#ebdbb2','#bdae93','#504945','#fe8019','#fabd2f','#b8bb26','#fb4934','#282828',H('#282828')),
  style=dict(ED_STYLE,**{'--font-mono':'"Fira Code",'+MONO_FB}),
  fonts='Space Grotesk / Figtree / Fira Code',
  gf='Space+Grotesk:wght@400;600&family=Figtree:ital,wght@0,400;0,600;1,400&family=Fira+Code:wght@400;600'),
]
# ---- contrast check
def lum(h):
    h=h.lstrip('#'); r,g,b=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    f=lambda c: c/12.92 if c<=.03928 else ((c+.055)/1.055)**2.4
    return .2126*f(r)+.7152*f(g)+.0722*f(b)
def cr(a,b):
    la,lb=sorted([lum(a),lum(b)],reverse=True); return (la+.05)/(lb+.05)
for t in themes:
    for mode in ('light','dark'):
        c=t[mode]
        if not c: continue
        chk=[('ink/paper',c['--ink'],c['--paper'],4.5),('ink/surface',c['--ink'],c['--surface'],4.5),('muted/paper',c['--muted'],c['--paper'],4.5),('muted/surface',c['--muted'],c['--surface'],4.5),
             ('accent/surface',c['--accent'],c['--surface'],4.5),('accent/paper',c['--accent'],c['--paper'],4.5),('accentink/accent',c['--accent-ink'],c['--accent'],4.5),
             ('good/surface',c['--good'],c['--surface'],3),('bad/surface',c['--bad'],c['--surface'],3),('hlink/hl',c['--hl-ink'],c['--hl'],4.5)]
        for n,a,b,m in chk:
            r=cr(a,b)
            if r<m: print('LOW',t['slug'],mode,n,round(r,2))
# ---- css files
def decl(d,ind='  '): return ''.join(f'{ind}{k}: {v};\n' for k,v in d.items())
def dropin(t):
    base=dict(t['style']); base.update(t['light'])
    for k,v in {'--texture':'none','--texture-size':'auto','--shadow':'none','--body-scale':'1'}.items(): base.setdefault(k,v)
    s=f"/* {t['name']} ({t['slug']})\n   {t['mood']}\n   Best for: {t['best']}\n   Fonts: {t['fonts']}\n   Google Fonts: https://fonts.googleapis.com/css2?family={t['gf']}&display=swap\n"
    if t['src']:
        sc=SOURCES[t['src']]
        s+=f"   Source: {sc['url']}\n   File: {files_text(t['src'])}\n   License: {sc['license']}\n"
        if t.get('srcnote'): s+=f"   Note: {t['srcnote']}\n"
    s+=f"   Mode: {'single. '+t['single'] if t['single'] else 'light and dark'}\n   --sketch is the feDisplacementMap scale for hand-drawn wobble (0 = off).\n*/\n"
    s+=':root {\n'+decl(base)+'}\n'
    if t['dark']:
        s+='@media (prefers-color-scheme: dark) {\n  :root:not([data-theme="light"]) {\n'+decl(t['dark'],'    ')+'  }\n}\n'
        s+=':root[data-theme="dark"] {\n'+decl(t['dark'])+'}\n'
    return s
def scoped(t):
    base=dict(t['style']); base.update(t['light'])
    for k,v in {'--texture':'none','--texture-size':'auto','--shadow':'none','--body-scale':'1'}.items(): base.setdefault(k,v)
    c='.t-'+t['slug']
    s=c+'{'+decl(base,'')+'}\n'
    if t['dark']:
        s+='@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) '+c+'{'+decl(t['dark'],'')+'}}\n'
        s+=':root[data-theme="dark"] '+c+'{'+decl(t['dark'],'')+'}\n'
    return s
for t in themes:
    open(f"{OUT}/themes/{t['slug']}.css",'w').write(dropin(t))
# ---- scene
def scene(slug):
    xs=[30+40*i for i in range(8)]
    o=[f'<svg class="scene" viewBox="0 0 340 142" role="img" aria-label="Eight commits in a row. c1 to c4 are good, c6 to c8 are bad, c5 is untested. The test pointer is on c5. The suspects are c5 and c6.">']
    o.append(f'<defs><filter id="sk-{slug}" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="7"/><feDisplacementMap in="SourceGraphic" scale="0" xChannelSelector="R" yChannelSelector="G"/></filter></defs>')
    o.append(f'<g class="shapes" data-filter="sk-{slug}">')
    o.append('<rect class="sus" x="169" y="50" width="82" height="60"/>')
    o.append('<line class="rail" x1="30" y1="72" x2="310" y2="72"/>')
    for i,x in enumerate(xs):
        k='good' if i<4 else ('unk' if i==4 else 'bad')
        o.append(f'<rect class="node {k}" x="{x-13}" y="59" width="26" height="26" rx="13"/>')
        if k=='good': o.append(f'<path class="glyph good" d="M{x-6} {72} l4 5 l8 -10"/>')
        elif k=='bad': o.append(f'<path class="glyph bad" d="M{x-5} 67 l10 10 M{x+5} 67 l-10 10"/>')
    o.append('<path class="ptr" d="M190 27 V48 M184 42 l6 7 l6 -7"/>')
    o.append('<path class="brk good" d="M20 116 v5 h140 v-5"/><path class="brk bad" d="M260 116 v5 h60 v-5"/>')
    o.append('</g>')
    o.append('<text class="unkq" x="190" y="77">?</text>')
    for i,x in enumerate(xs): o.append(f'<text class="lbl" x="{x}" y="102">c{i+1}</text>')
    o.append('<text class="ptrl" x="190" y="20">test</text>')
    o.append('<text class="grp" x="90" y="136">good</text><text class="grp" x="290" y="136">bad</text>')
    o.append('<text class="grp strong" x="210" y="126">suspects</text>')
    o.append('</svg>')
    return ''.join(o)
def card(i,t):
    e=html.escape
    sw=''.join(f'<span class="sw" style="background:var({k})" title="{k}"><i>{k[2:]}</i></span>' for k in ['--paper','--surface','--ink','--muted','--line','--accent','--hl','--good','--bad'])
    hand=''.join(f'<span class="{"on" if j<t["hand"] else ""}"></span>' for j in range(5))
    mode=f'<span class="badge">{e(t["single"])}</span>' if t['single'] else '<span class="badge">Light and dark</span>'
    return f'''<article class="theme" id="{t['slug']}">
<div class="sample t-{t['slug']}">
  <p class="kicker">Step 3 of 5</p>
  <h3>Halve the suspects</h3>
  <figure>{scene(t['slug'])}<figcaption>c6 fails. The bug is c5 or c6.</figcaption></figure>
  <p class="prose">Each test cuts the suspect range in half. Seven suspects need three tests, not six. One more test on <b>c5</b> names the commit.</p>
  <pre class="code"><code><span class="pr">$</span> git bisect start c8 c1</code></pre>
  <div class="ctl"><button type="button" class="ghost">Back</button><button type="button" class="next">Next</button><span class="dots"><i></i><i></i><i class="on"></i><i></i><i></i></span></div>
</div>
<div class="meta">
  <h2><span class="num">{i:02d}</span> {e(t['name'])}</h2>
  <p class="mood">{e(t['mood'])}</p>
  <dl>
    <dt>Best for</dt><dd>{e(t['best'])}</dd>
    <dt>Fonts</dt><dd>{e(t['fonts'])} <small>(display / body / mono)</small></dd>
    <dt>Palette</dt><dd><div class="sws t-{t['slug']}">{sw}</div>{mode}</dd>
    <dt>Hand-drawn</dt><dd><span class="hand">{hand}</span> {t['hand']}/5</dd>
    <dt>Risk</dt><dd>{e(t['risk'])}</dd>
    <dt>File</dt><dd><code>themes/{t['slug']}.css</code></dd>
  </dl>
</div>
</article>'''
_seen=set();_fam=[]
for t in themes:
    for f in t['gf'].split('&family='):
        n=f.split(':')[0]
        if n not in _seen: _seen.add(n); _fam.append(f)
gf='&family='.join(_fam)
css_scoped=''.join(scoped(t) for t in themes)
cards='\n'.join(card(i+1,t) for i,t in enumerate(themes))
page=f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Explainer themes: 25 drafts</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family={gf}&display=swap" rel="stylesheet">
<style>
/* gallery chrome */
:root{{--g-bg:#e4e5e7;--g-card:#ffffff;--g-ink:#15171a;--g-muted:#555a63;--g-line:#c9ccd1;--g-mark:#15171a;color-scheme:light}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--g-bg:#0e0f11;--g-card:#17191c;--g-ink:#eceef0;--g-muted:#a3a8b0;--g-line:#2e3136;--g-mark:#eceef0;color-scheme:dark}}}}
:root[data-theme="dark"]{{--g-bg:#0e0f11;--g-card:#17191c;--g-ink:#eceef0;--g-muted:#a3a8b0;--g-line:#2e3136;--g-mark:#eceef0;color-scheme:dark}}
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--g-bg);color:var(--g-ink);font:16px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;overflow-wrap:anywhere}}
.wrap{{max-width:1120px;margin:0 auto;padding:16px 14px 64px}}
header.top{{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin:6px 0 14px}}
header.top h1{{font-size:1.5rem;line-height:1.15;margin:0;letter-spacing:-.02em}}
header.top p{{margin:.3rem 0 0;color:var(--g-muted);font-size:.92rem}}
#mode{{flex:none;font:inherit;font-size:.85rem;font-weight:600;padding:9px 12px;min-height:44px;border:2px solid var(--g-mark);background:transparent;color:var(--g-ink);border-radius:999px;cursor:pointer}}
.rec{{background:var(--g-card);border:1px solid var(--g-line);border-left:6px solid var(--g-mark);padding:14px 16px;margin:0 0 14px}}
.rec h2{{font-size:1rem;margin:0 0 .4rem;text-transform:uppercase;letter-spacing:.08em}}
.rec ol{{margin:.4rem 0 .5rem;padding-left:1.3rem}}
.rec li{{margin:.35rem 0}}
.rec p{{margin:.4rem 0;color:var(--g-muted);font-size:.92rem}}
.rec a,.jump a{{color:inherit}}
.jump{{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 22px;padding:0;list-style:none}}
.jump a{{display:block;padding:7px 11px;border:1px solid var(--g-line);background:var(--g-card);border-radius:999px;font-size:.85rem;text-decoration:none}}
.grid{{display:grid;gap:30px;grid-template-columns:minmax(0,1fr)}}
@media (min-width:900px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr));gap:34px 26px}}}}
.theme{{min-width:0;scroll-margin-top:12px}}
.meta{{padding:14px 2px 0}}
.meta h2{{margin:0;font-size:1.25rem;letter-spacing:-.01em}}
.meta .num{{font:600 .8rem ui-monospace,Menlo,monospace;color:var(--g-muted);margin-right:4px}}
.meta .mood{{margin:.15rem 0 .6rem;color:var(--g-muted)}}
.meta dl{{display:grid;grid-template-columns:88px minmax(0,1fr);gap:7px 10px;margin:0;font-size:.9rem}}
.meta dt{{color:var(--g-muted);font-size:.74rem;text-transform:uppercase;letter-spacing:.07em;padding-top:.2em}}
.meta dd{{margin:0;min-width:0}}
.meta small{{color:var(--g-muted)}}
.meta code{{font:.85em ui-monospace,Menlo,monospace}}
.sws{{display:grid;grid-template-columns:repeat(9,minmax(0,1fr));gap:3px;background:none!important;max-width:330px}}
.sw{{display:block;aspect-ratio:1;border:1px solid var(--g-line);border-radius:3px;position:relative}}
.sw i{{position:absolute;left:0;right:0;top:calc(100% + 2px);font:normal 8px/1 ui-monospace,Menlo,monospace;color:var(--g-muted);text-align:center;overflow:hidden;white-space:nowrap}}
.badge{{display:inline-block;margin-top:16px;font-size:.78rem;color:var(--g-muted);border:1px solid var(--g-line);border-radius:999px;padding:1px 9px}}
.hand{{display:inline-flex;gap:3px;vertical-align:middle;margin-right:4px}}
.hand span{{width:11px;height:11px;border:1.5px solid var(--g-mark);border-radius:50%}}
.hand span.on{{background:var(--g-mark)}}
/* theme tokens, scoped per sample */
{css_scoped}
/* shared sample structure: reads tokens only */
.sample{{background-color:var(--paper);background-image:var(--texture);background-size:var(--texture-size);color:var(--ink);font-family:var(--font-body);font-size:calc(1.02rem * var(--body-scale));line-height:1.5;padding:18px 16px 20px;border:var(--border-width) solid var(--line);border-radius:var(--radius);overflow:hidden}}
.sample .kicker{{margin:0;font-family:var(--font-mono);font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}}
.sample h3{{margin:.1rem 0 .7rem;font-family:var(--font-display);font-weight:var(--display-weight);font-size:calc(1.4rem * var(--display-scale));line-height:1.08;letter-spacing:var(--display-tracking);text-transform:var(--display-transform);color:var(--ink)}}
.sample figure{{margin:0 0 .9rem;background:var(--surface);border:var(--border-width) solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:10px 6px 0}}
.sample .scene{{display:block;width:100%;height:auto}}
.sample figcaption{{margin:6px -6px 0;padding:9px 12px;border-top:var(--border-width) solid var(--line);font-weight:600;font-size:.98em}}
.sample figcaption::before{{content:"";display:inline-block;width:.6em;height:.6em;margin-right:.5em;background:var(--hl);border:1px solid var(--ink);border-radius:var(--radius)}}
.sample .prose{{margin:0 0 .8rem}}
.sample .prose b{{background:color-mix(in srgb,var(--hl) 45%,transparent);padding:0 .2em;font-weight:600}}
.sample .code{{margin:0 0 1rem;padding:9px 12px;background:var(--surface);border:var(--border-width) solid var(--line);border-left:4px solid var(--accent);border-radius:var(--radius);font-family:var(--font-mono);font-size:.84rem;white-space:pre-wrap;color:var(--ink)}}
.sample .code code{{font:inherit}}
.sample .code .pr{{color:var(--muted)}}
.sample .ctl{{display:flex;align-items:center;gap:10px}}
.sample button{{font-family:var(--font-display);font-weight:var(--display-weight);font-size:calc(.95rem * var(--display-scale));letter-spacing:var(--display-tracking);text-transform:var(--display-transform);min-height:44px;padding:6px 18px;border-radius:var(--radius);border:var(--border-width) solid var(--ink);cursor:pointer;line-height:1}}
.sample .ghost{{background:transparent;color:var(--ink)}}
.sample .next{{background:var(--accent);color:var(--accent-ink);border-color:var(--accent);box-shadow:var(--shadow)}}
.sample .dots{{margin-left:auto;display:flex;gap:5px}}
.sample .dots i{{width:9px;height:9px;border:1.5px solid var(--muted);border-radius:var(--radius)}}
.sample .dots i.on{{background:var(--hl);border-color:var(--ink)}}
/* scene */
.scene .shapes *{{fill:none;stroke-width:var(--stroke-width);stroke-linecap:var(--linecap);stroke-linejoin:round}}
.scene .rail{{stroke:var(--muted)}}
.scene .node{{fill:var(--surface);rx:var(--node-rx)}}
.scene .node.good,.scene .glyph.good,.scene .brk.good{{stroke:var(--good)}}
.scene .node.bad,.scene .glyph.bad,.scene .brk.bad{{stroke:var(--bad)}}
.scene .node.unk{{stroke:var(--ink);stroke-dasharray:4 3}}
.scene .sus{{fill:color-mix(in srgb,var(--hl) 30%,transparent)!important;stroke:var(--hl);stroke-dasharray:6 4;rx:var(--radius)}}
.scene .ptr{{stroke:var(--accent)}}
.scene .brk{{stroke-width:calc(var(--stroke-width) * .6)!important}}
.scene text{{text-anchor:middle;font-family:var(--font-mono);font-size:11px;fill:var(--ink)}}
.scene .unkq{{font-weight:700;font-size:13px}}
.scene .ptrl{{fill:var(--accent);font-family:var(--font-display);font-size:calc(12px * var(--display-scale));font-weight:var(--display-weight);letter-spacing:var(--display-tracking);text-transform:var(--display-transform)}}
.scene .grp{{fill:var(--muted);font-size:10px}}
.scene .grp.strong{{fill:var(--ink);font-weight:700}}
</style>
</head>
<body>
<div class="wrap">
<header class="top">
  <div><h1>Explainer themes</h1><p>Twenty-five draft design languages, including three Catppuccin flavors and twelve editor color schemes. Same bisect sample in each.</p></div>
  <button id="mode" type="button" aria-label="Switch color mode">Mode: auto</button>
</header>
<section class="rec">
  <h2>My top three for you</h2>
  <ol>
    <li><b><a href="#inkwell">Inkwell</a>.</b> It looks like your own notebook. Your drawings fit without redrawing, and the green highlighter is a mark people will remember.</li>
    <li><b><a href="#whiteprint">Whiteprint</a>.</b> The best fit for low-level and CI topics. Exact lines suit memory layouts and pipelines, and engineers trust it on sight.</li>
    <li><b><a href="#two-ink">Two-Ink</a>.</b> The most recognizable in a feed. Navy and pink read well in 9:16 reels and look like nobody else's AI output.</li>
  </ol>
  <p>If you want one house look, take Inkwell and borrow Whiteprint's grid for dense diagrams. Skip Dry Erase as a signature: it is pleasant but common. Phosphor and Slate are dark only on purpose, so the toggle does not change them.</p>
  <p><b>New: Catppuccin.</b> The open-source (MIT) pastel palette, using only its official colors, checked against the @catppuccin/palette package v1.8.0. <a href="#catppuccin">Catppuccin</a> switches between Latte (light) and Mocha (dark) with the toggle. <a href="#catppuccin-frappe">Frappé</a> and <a href="#catppuccin-macchiato">Macchiato</a> are the other two dark flavors. A good fit for agent and tooling topics, since many readers already use it in their editor.</p>
  <p><b>New: Editor color schemes.</b> Twelve schemes from the list in Nathan Long, <a href="https://nathan-long.com/blog/colorschemes-for-the-discerning-developer/">"Colorschemes for the discerning developer"</a>: <a href="#rose-pine">Rosé Pine</a>, <a href="#tokyo-night">Tokyo Night</a>, <a href="#dracula">Dracula</a>, <a href="#nord">Nord</a>, <a href="#solarized">Solarized</a>, <a href="#oceanic-next">Oceanic Next</a>, <a href="#tomorrow">Tomorrow</a>, <a href="#iceberg">Iceberg</a>, <a href="#one-half">One Half</a>, <a href="#kanagawa">Kanagawa</a>, <a href="#onedark">OneDark</a> and <a href="#gruvbox">Gruvbox</a>. Every color comes from the scheme's own source palette, and each CSS file names the source file and license. Nord and Oceanic Next are dark only, since their sources define no light palette. The others switch between their light and dark variants with the toggle.</p>
</section>
<ul class="jump">{''.join(f'<li><a href="#{t["slug"]}">{html.escape(t["name"])}</a></li>' for t in themes)}</ul>
<main class="grid">
{cards}
</main>
</div>
<script>
(function(){{
  var root=document.documentElement,btn=document.getElementById('mode'),order=['auto','light','dark'],cur='auto';
  function sketch(){{
    document.querySelectorAll('.sample').forEach(function(s){{
      var v=parseFloat(getComputedStyle(s).getPropertyValue('--sketch'))||0,g=s.querySelector('.shapes'),id=g.getAttribute('data-filter');
      s.querySelector('feDisplacementMap').setAttribute('scale',v);
      if(v>0)g.setAttribute('filter','url(#'+id+')');else g.removeAttribute('filter');
    }});
  }}
  btn.addEventListener('click',function(){{
    cur=order[(order.indexOf(cur)+1)%3];
    if(cur==='auto')root.removeAttribute('data-theme');else root.setAttribute('data-theme',cur);
    btn.textContent='Mode: '+cur;sketch();
  }});
  sketch();
}})();
</script>
</body>
</html>'''
open(OUT+'/index.html','w').write(page)
print('ok',len(page))
