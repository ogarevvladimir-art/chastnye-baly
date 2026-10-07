"""Сверка пилота (этап 2): кадры сайта, соответствующие кадрам Figma шапки, меню и Hero → Форматы.

  python tools/pilot_shots.py                 # всё → сверка/hero, сверка/меню
  python tools/pilot_shots.py --only menu

Десктоп снимается в окне 1440 × 932 (высота кадра Figma), телефон 390 × 844, планшет 834 × 1194.
Ленивые картинки грузятся заранее. Раскадровка входа — WAAPI на паузе в нужный момент времени (0 / 25 / 100 %).
"""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve, url_for

STILL = "*,*::before,*::after{transition-duration:0s!important;transition-delay:0s!important;scroll-behavior:auto!important}"


def eager(page):
    page.evaluate("""async () => {
        document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager');
        await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
        await document.fonts.ready;
    }""")


def new_page(browser, base, w, h, reduced=True):
    ctx = browser.new_context(viewport={"width": w, "height": h},
                              reduced_motion="reduce" if reduced else "no-preference")
    page = ctx.new_page()
    page.goto(url_for(base, "site/index.html"), wait_until="networkidle")
    eager(page)
    return ctx, page


def freeze_at(page, t_ms):
    """Все анимации страницы — на паузу в момент t (мс от старта)."""
    page.evaluate("t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t; })", t_ms)


def hero_formats(browser, base, out):
    # Десктоп: покой hero (C · 1), шов (C · 2: слово у шва — прокрутка на путь слова), покой Форматов, наведения
    ctx, page = new_page(browser, base, 1440, 932)
    page.add_style_tag(content=STILL)
    page.wait_for_timeout(200)
    page.screenshot(path=str(out / "v2_d_hero.png"))
    travel = page.evaluate("""() => { const t = document.querySelector('.hf__track'), w = document.querySelector('.hf__word');
        return Math.round(t.getBoundingClientRect().bottom - w.getBoundingClientRect().bottom); }""")
    page.evaluate("y => scrollTo(0, y)", travel)
    page.wait_for_timeout(200)
    page.screenshot(path=str(out / "v2_d_seam.png"))
    top = page.evaluate("document.querySelector('#formats').getBoundingClientRect().top + scrollY")
    page.evaluate("y => scrollTo(0, y)", top)
    page.wait_for_timeout(200)
    page.screenshot(path=str(out / "v2_d_formats.png"))
    page.mouse.move(300, 600)
    page.wait_for_timeout(200)
    page.screenshot(path=str(out / "v2_d_formats_private.png"))
    page.mouse.move(1200, 600)
    page.wait_for_timeout(200)
    page.screenshot(path=str(out / "v2_d_formats_corp.png"))
    print("десктоп: путь слова", travel, "px")
    ctx.close()

    # Телефон и планшет: блок целиком
    for w, h, name in ((390, 844, "m"), (834, 1194, "t"), (360, 780, "m360")):
        ctx, page = new_page(browser, base, w, h)
        page.add_style_tag(content=STILL)
        page.locator(".hf").screenshot(path=str(out / f"v2_{name}_block.png"))
        ctx.close()

    # Вход по времени: телефон окно 1,3 с, планшет 1,1 с (заметки 229:1127, 254:2478)
    for w, h, name, window in ((390, 844, "m", 1300), (834, 1194, "t", 1100), (1440, 932, "d", 1300)):
        for pct in (0, 25, 100):
            ctx, page = new_page(browser, base, w, h, reduced=False)
            page.wait_for_function("document.getAnimations().length > 0")
            freeze_at(page, window * pct / 100)
            page.wait_for_timeout(50)
            page.screenshot(path=str(out / f"v2_{name}_in{pct}.png"))
            ctx.close()


def menu(browser, base, out):
    for w, h, name in ((390, 844, "m"), (834, 1194, "t"), (1440, 932, "d")):
        ctx, page = new_page(browser, base, w, h)
        page.add_style_tag(content=STILL)
        page.click(".site-header__menu")
        page.wait_for_timeout(300)
        page.screenshot(path=str(out / f"v2_{name}_menu_open.png"))
        if name == "d":
            page.hover(".menu__list li:nth-child(1) .menu__item")
            page.wait_for_timeout(200)
            page.screenshot(path=str(out / "v2_d_menu_h01.png"))
        ctx.close()

    # Раскадровка открытия 25 % (0,175 с) и закрытия 50 % (0,375 с) на телефоне — по кадрам 229:1220 / 229:1254
    ctx, page = new_page(browser, base, 390, 844, reduced=False)
    page.click(".site-header__menu")
    page.wait_for_timeout(1)
    page.evaluate("""() => document.getAnimations().forEach(a => { a.pause(); a.currentTime = 175; })""")
    page.screenshot(path=str(out / "v2_m_menu_25.png"))
    ctx.close()
    ctx, page = new_page(browser, base, 390, 844, reduced=False)
    page.wait_for_timeout(1500)
    page.click(".site-header__menu")
    page.wait_for_timeout(900)
    page.keyboard.press("Escape")
    page.evaluate("() => document.getAnimations().forEach(a => { a.pause(); a.currentTime = 375; })")
    page.screenshot(path=str(out / "v2_m_menu_close50.png"))
    ctx.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", choices=["hero", "menu"])
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    args = ap.parse_args()
    suffix = "" if args.browser == "chromium" else "_webkit"
    with serve() as base, sync_playwright() as pw:
        browser = getattr(pw, args.browser).launch()
        if args.only in (None, "hero"):
            out = SVERKA / ("hero" + suffix)
            out.mkdir(parents=True, exist_ok=True)
            hero_formats(browser, base, out)
        if args.only in (None, "menu"):
            out = SVERKA / ("меню" + suffix)
            out.mkdir(parents=True, exist_ok=True)
            menu(browser, base, out)
        browser.close()


if __name__ == "__main__":
    main()
