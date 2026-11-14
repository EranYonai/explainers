import os
from playwright.sync_api import sync_playwright
# Screenshots go to out/themes/ at the repo root (ignored by git).
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','out','themes')
os.makedirs(OUT,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch()
    for name,w,h,scheme in [('phone',390,844,'light'),('phone-dark',390,844,'dark'),('desk',1100,900,'light')]:
        pg=b.new_page(viewport={'width':w,'height':h},color_scheme=scheme)
        fails=[]
        pg.on('requestfailed',lambda r:fails.append(r.url[:80]))
        pg.on('console',lambda m:print('console',m.text) if m.type=='error' else None)
        pg.goto('file://'+os.path.join(os.path.dirname(os.path.abspath(__file__)),'index.html'),wait_until='networkidle')
        pg.wait_for_timeout(800)
        print(name,'scrollWidth',pg.evaluate('document.documentElement.scrollWidth'),'fails',len(fails),fails[:2],
              'fonts',pg.evaluate('[...document.fonts].filter(f=>f.status=="loaded").length'))
        pg.screenshot(path=os.path.join(OUT,f'{name}.png'),full_page=True)
    b.close()
