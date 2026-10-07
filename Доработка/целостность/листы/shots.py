from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://127.0.0.1:8080/site/',wait_until='networkidle')
    pg.wait_for_timeout(1500)
    info=pg.evaluate("""()=>[...document.querySelectorAll('main > section, body > section, section')].filter(s=>!s.parentElement.closest('section')).map(s=>({c:s.className,y:s.getBoundingClientRect().top+scrollY,h:s.offsetHeight,head:(s.querySelector('h1,h2')||{}).textContent}))""")
    print(json.dumps(info,ensure_ascii=False,indent=0))
    total=pg.evaluate("document.documentElement.scrollHeight")
    y=0;i=0
    while y<total:
        pg.evaluate(f"window.scrollTo(0,{y})");pg.wait_for_timeout(700)
        pg.screenshot(path=f"v{i:03d}.png");i+=1;y+=850
    print(total,i)
    b.close()
