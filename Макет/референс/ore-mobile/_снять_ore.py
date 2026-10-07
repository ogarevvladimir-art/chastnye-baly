# Съёмка ore.co на телефоне (390 × 844, iPhone UA). Запускать из этой папки:
#   python _снять_ore.py [all|pages|menu|form|scroll]
# pages  — листание главной 390 и 834 (съёмка 2026-09-29; файлы ore_m_*/ore_t_* переименованы в 390_*/834_*)
# menu   — меню: покой, кадры открытия, тап по пункту, закрытие   → 390_menu_*.jpg, 390_menu_замер.json
# form   — форма «contact us»: пустая, фокус, ввод                 → 390_form_*.jpg, 390_form_*замер.json
# scroll — видео скролла главной + замер анимированных элементов   → 390_scroll.webm, 390_scroll_track.json
# all    — menu + form + scroll (pages отдельно)
import asyncio, json, sys, os
from playwright.async_api import async_playwright

UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
URL = "https://ore.co"
VW, VH = 390, 844
WHAT = sys.argv[1] if len(sys.argv) > 1 else "all"

# видимые текстовые и управляющие элементы с размерами и типографикой
VISIBLE = r"""()=>{const out=[];document.querySelectorAll('a,button,input,textarea,select,label,h1,h2,h3,h4,p,span,div').forEach(e=>{
 const b=e.getBoundingClientRect();if(b.width==0||b.bottom<0||b.top>innerHeight)return;const cs=getComputedStyle(e);
 if(cs.visibility=='hidden'||+cs.opacity==0)return;
 const own=[...e.childNodes].filter(n=>n.nodeType==3).map(n=>n.textContent).join('').trim();
 const t=own||e.placeholder||e.value||'';
 if(!t&&!['INPUT','TEXTAREA','BUTTON','SELECT'].includes(e.tagName))return;
 out.push({tag:e.tagName,cls:(e.className||'').toString().slice(0,60),text:t.slice(0,50),x:Math.round(b.x),y:Math.round(b.y),
  w:Math.round(b.width),h:Math.round(b.height),fs:cs.fontSize,lh:cs.lineHeight,ls:cs.letterSpacing,ff:cs.fontFamily.split(',')[0],
  color:cs.color,bg:cs.backgroundColor,border:cs.borderBottom,op:cs.opacity,tr:cs.transform})});return out}"""

# элементы, которые двигаются от скролла: sticky/fixed, transform, opacity, clip-path
TRACK = r"""()=>{const r=[];document.querySelectorAll('body *').forEach((e,i)=>{if(e.closest('script,style,svg'))return;
 const cs=getComputedStyle(e);const b=e.getBoundingClientRect();if(b.width<20||b.height<8)return;
 const sticky=cs.position=='sticky'||cs.position=='fixed';
 const anim=cs.transform!='none'||+cs.opacity<1||cs.clipPath!='none';
 if(!sticky&&!anim)return;if(!e.dataset.trk)e.dataset.trk=i;
 r.push([e.dataset.trk,e.tagName,(e.className||'').toString().slice(0,40),(e.innerText||e.getAttribute('alt')||'').trim().slice(0,24).replace(/\n/g,' '),
  Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height),cs.transform=='none'?'':cs.transform,(+cs.opacity).toFixed(2),
  cs.clipPath=='none'?'':cs.clipPath.slice(0,40),cs.letterSpacing,cs.position])});return r}"""


async def ctx_new(b, **kw):
    return await b.new_context(viewport={"width": VW, "height": VH}, device_scale_factor=2, is_mobile=True,
                               has_touch=True, user_agent=UA, **kw)


async def open_home(pg):
    try:
        await pg.goto(URL, wait_until="networkidle", timeout=45000)
    except Exception as e:
        print("goto", e)
    await pg.wait_for_timeout(3000)


async def shot(pg, name):
    await pg.screenshot(path=name, type="jpeg", quality=80)
    print("  ", name)


async def shots_at(pg, prefix, moments):
    """Кадры в заданные моменты (мс) от текущего события."""
    t = 0
    for ms in moments:
        await pg.wait_for_timeout(ms - t); t = ms
        await shot(pg, f"{prefix}_{ms:04d}ms.jpg")


def dump(obj, name):
    with open(name, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


async def pages(b):
    for name, vw, vh in [("m", 390, 844), ("t", 834, 1194)]:
        ctx = await b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=2, is_mobile=True,
                                  has_touch=True, user_agent=UA)
        pg = await ctx.new_page(); await open_home(pg)
        y = i = 0; h = await pg.evaluate("document.documentElement.scrollHeight")
        while y < h and i < 40:
            await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(900)
            await pg.screenshot(path=f"ore_{name}_{i:02d}.jpg", type="jpeg", quality=70)
            y += int(vh * 0.9); i += 1; h = await pg.evaluate("document.documentElement.scrollHeight")
        await ctx.close()


async def menu(b):
    ctx = await ctx_new(b); pg = await ctx.new_page(); await open_home(pg)
    await shot(pg, "390_menu_0_закрыто.jpg")
    await pg.tap("button.hamburger")
    await shots_at(pg, "390_menu_1_открытие", (80, 200, 400, 700, 1200))
    await pg.wait_for_timeout(1000)
    await shot(pg, "390_menu_2_открыто.jpg")
    dump(await pg.evaluate(VISIBLE), "390_menu_замер.json")
    # тап по пункту CUSTOM: нажатие (touchstart) и переход
    item = pg.locator("a.nav-item").nth(1)
    await item.dispatch_event("touchstart"); await pg.wait_for_timeout(250)
    await shot(pg, "390_menu_3_тап_нажатие.jpg")
    await item.tap()
    await shots_at(pg, "390_menu_4_после_тапа", (150, 450, 900, 2000))
    print("  url после тапа:", pg.url)
    # закрытие меню
    await open_home(pg); await pg.tap("button.hamburger"); await pg.wait_for_timeout(1500)
    await pg.tap("button.hamburger")
    await shots_at(pg, "390_menu_5_закрытие", (150, 450, 900))
    await ctx.close()


async def form(b):
    ctx = await ctx_new(b); pg = await ctx.new_page(); await open_home(pg)
    link = pg.get_by_text("contact us", exact=True).last
    await link.scroll_into_view_if_needed(); await pg.wait_for_timeout(1500)
    await shot(pg, "390_form_0_подвал.jpg")
    await link.tap()
    await shots_at(pg, "390_form_1_открытие", (150, 450, 900))
    await pg.wait_for_timeout(1500)
    await shot(pg, "390_form_2_пустая.jpg")
    dump(await pg.evaluate(VISIBLE), "390_form_замер.json")
    inp = pg.locator("input:visible, textarea:visible").first
    if await inp.count():
        await inp.tap(); await pg.wait_for_timeout(700)
        await shot(pg, "390_form_3_фокус.jpg")
        dump(await pg.evaluate(VISIBLE), "390_form_фокус_замер.json")
        await inp.type("Anna", delay=60); await pg.wait_for_timeout(400)
        await shot(pg, "390_form_4_ввод.jpg")
        await pg.evaluate("document.activeElement.blur()")
        for k in range(1, 4):                                 # форма ниже первого экрана
            await pg.mouse.wheel(0, VH * 0.8); await pg.wait_for_timeout(700)
            await shot(pg, f"390_form_5_ниже_{k}.jpg")
    else:
        print("  полей формы не найдено")
    await ctx.close()


async def scroll(b):
    os.makedirs("_video", exist_ok=True)
    ctx = await ctx_new(b, record_video_dir="_video", record_video_size={"width": VW, "height": VH})
    pg = await ctx.new_page(); await open_home(pg)
    H = await pg.evaluate("document.documentElement.scrollHeight"); print("  scrollHeight", H)
    track, y = [], 0
    while y <= H - VH:                     # шаг 10 px каждые ~16 мс ≈ 600 px/с — спокойный палец
        await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(16)
        if y % 40 == 0:
            await pg.wait_for_timeout(120)  # дать анимации доехать до замера
            track.append({"y": y, "els": await pg.evaluate(TRACK)})
        y += 10
        H = await pg.evaluate("document.documentElement.scrollHeight")
    await pg.wait_for_timeout(1500)
    with open("390_scroll_track.json", "w", encoding="utf-8") as f:
        json.dump(track, f, ensure_ascii=False)
    vpath = await pg.video.path(); await ctx.close()
    os.replace(vpath, "390_scroll.webm"); os.rmdir("_video")
    print("  390_scroll.webm, замеров:", len(track))


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, fn in [("pages", pages), ("menu", menu), ("form", form), ("scroll", scroll)]:
            if WHAT == name or (WHAT == "all" and name != "pages"):
                print(name); await fn(b)
        await b.close()

asyncio.run(main())
