"""Сверка этапа 3 (01 Подготовка, 02 Вечер, 03 Музыка, 04 Танцмейстер): кадры сайта под кадры Figma и пары «Figma | сайт».

  python tools/stage3_shots.py                  # все блоки → сверка/<блок>/
  python tools/stage3_shots.py --only prep -b webkit

Покой — секция целиком на 390 / 834 / 1440 (окно 844 / 1194 / 932), шапка сайта скрыта (в кадрах Figma своя).
Десктоп: наведения 01 / 03 / 04 — мышью; шаги 02 — прокрутка до положения пункта в окне 1440 × 1032
(сцена = 960, как в кадре). Рендеры Figma — _figma/v3/. Пары — через pair.py.
"""
import argparse
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from _serve import SVERKA, TOOLS, VERSTKA, serve, url_for

FIG = VERSTKA / "_figma" / "v3"
STILL = ("*,*::before,*::after{transition-duration:0s!important;transition-delay:0s!important;scroll-behavior:auto!important}"
         ".site-header,.skip{visibility:hidden!important}")
HEIGHTS = {390: 844, 834: 1194, 1440: 932}


def page_at(browser, base, w, h=None):
    ctx = browser.new_context(viewport={"width": w, "height": h or HEIGHTS[w]}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(url_for(base, "site/index.html"), wait_until="networkidle")
    page.add_style_tag(content=STILL)
    page.evaluate("""async () => {
        document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager');
        await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
        await document.fonts.ready;
    }""")
    page.wait_for_timeout(150)
    return ctx, page


def shot(page, sel, path):
    page.locator(sel).first.screenshot(path=str(path))


def pair(fig, site, out):
    if Path(fig).exists() and Path(site).exists():
        subprocess.run([sys.executable, str(TOOLS / "pair.py"), str(fig), str(site), "-o", str(out)], check=True)


def scroll_to(page, sel, dy=0):
    page.evaluate("([s, dy]) => { const e = document.querySelector(s); scrollTo({ top: e.getBoundingClientRect().top + scrollY + dy, behavior: 'instant' }); }", [sel, dy])
    page.wait_for_timeout(120)


def rest(browser, base, name, sel, figs, out):
    """Секция целиком в окне её высоты: снимок без прокрутки (длинный снимок элемента не дорисовывает ленту карусели)."""
    for w, fig in figs.items():
        ctx, page = page_at(browser, base, w)
        h = page.evaluate("s => document.querySelector(s).getBoundingClientRect().height", sel)
        page.set_viewport_size({"width": w, "height": int(h) + 2})
        page.wait_for_timeout(150)
        scroll_to(page, sel)
        b = page.locator(sel).first.bounding_box()
        p = out / f"site_{w}.png"
        page.screenshot(path=str(p), clip={"x": 0, "y": b["y"], "width": w, "height": b["height"]})
        pair(FIG / fig, p, out / f"pair_{w}.png")
        ctx.close()


def hover_states(browser, base, sel, parts, out, figs):
    """parts: [(имя, селектор части)], figs: {имя: файл Figma}. Окно выше секции: снимок без прокрутки, курсор не уходит."""
    ctx, page = page_at(browser, base, 1440, 1800)
    for name, psel in parts:
        scroll_to(page, sel)
        box = page.locator(psel).first.bounding_box()
        page.mouse.move(box["x"] + 40, box["y"] + 20)
        page.wait_for_timeout(200)
        b = page.locator(sel).first.bounding_box()
        p = out / f"site_1440_{name}.png"
        page.screenshot(path=str(p), clip={"x": 0, "y": b["y"], "width": 1440, "height": b["height"]})
        pair(FIG / figs[name], p, out / f"pair_1440_{name}.png")
    ctx.close()


def evening_steps(browser, base, out):
    """Шаги 02: прокрутка до середины отрезка пункта; кадр сцены против кадра Figma y 640…1600."""
    from PIL import Image
    ctx, page = page_at(browser, base, 1440, 1032)
    for n in range(1, 6):
        page.evaluate("""n => { const eve = document.querySelector('.eve'), st = eve.querySelector('.eve__stage');
            const top = parseFloat(getComputedStyle(st).top), travel = eve.offsetHeight - st.offsetHeight;
            const y = eve.getBoundingClientRect().top + scrollY - top + travel * (n - 1) / 4;
            scrollTo({ top: y, behavior: 'instant' }); }""", n)
        page.wait_for_timeout(250)
        p = out / f"site_1440_step{n}.png"
        shot(page, ".eve__stage", p)
        fig = out / f"_fig_step{n}.png"
        Image.open(FIG / f"v3_d_eve_{n}.png").crop((0, 640, 1440, 1600)).save(fig)
        pair(fig, p, out / f"pair_1440_step{n}.png")
    # шапка и финал десктопа
    head = out / "site_1440_head.png"
    scroll_to(page, "#evening")
    page.screenshot(path=str(head), clip={"x": 0, "y": 0, "width": 1440, "height": 640})
    fig = out / "_fig_head.png"
    Image.open(FIG / "v3_d_eve_1.png").crop((0, 0, 1440, 640)).save(fig)
    pair(fig, head, out / "pair_1440_head.png")
    fin = out / "site_1440_final.png"
    shot(page, ".eve__final", fin)
    fig = out / "_fig_final.png"
    Image.open(FIG / "v3_d_eve_1.png").crop((0, 1600, 1440, 2320)).save(fig)
    pair(fig, fin, out / "pair_1440_final.png")
    ctx.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", choices=["prep", "evening", "music", "dm"])
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    a = ap.parse_args()
    sfx = "" if a.browser == "chromium" else "_webkit"
    with serve() as base, sync_playwright() as pw:
        b = getattr(pw, a.browser).launch()

        def out(name):
            d = SVERKA / (name + sfx)
            d.mkdir(parents=True, exist_ok=True)
            return d

        if a.only in (None, "prep"):
            o = out("01")
            rest(b, base, "prep", "#prep", {390: "v3_m_prep.png", 834: "v3_t_prep.png", 1440: "v3_d_prep.png"}, o)
            hover_states(b, base, "#prep", [(f"h{i}", f".prep__step:nth-child({i}) .prep__word") for i in (1, 2, 5)], o,
                         {f"h{i}": f"v3_d_prep_h{i}.png" for i in (1, 2, 5)})
        if a.only in (None, "evening"):
            o = out("02")
            rest(b, base, "evening", "#evening", {390: "v3_m_eve.png", 834: "v3_t_eve.png"}, o)
            evening_steps(b, base, o)
        if a.only in (None, "music"):
            o = out("03")
            rest(b, base, "music", "#music", {390: "v3_m_music.png", 834: "v3_t_music.png", 1440: "v3_d_music_1.png"}, o)
            hover_states(b, base, "#music", [(f"s{i}", f'.music__card[data-i="{i}"] .music__title') for i in (2, 3)], o,
                         {f"s{i}": f"v3_d_music_{i}.png" for i in (2, 3)})
        if a.only in (None, "dm"):
            o = out("04")
            rest(b, base, "dm", "#dancemaster", {390: "v3_m_dm.png", 834: "v3_t_dm.png", 1440: "v3_d_dm.png"}, o)
            hover_states(b, base, "#dancemaster", [("h1", '[data-panel="spectators"] .dm__num'), ("h2", '[data-panel="participants"] .dm__num')], o,
                         {"h1": "v3_d_dm_h1.png", "h2": "v3_d_dm_h2.png"})
        b.close()


if __name__ == "__main__":
    main()
