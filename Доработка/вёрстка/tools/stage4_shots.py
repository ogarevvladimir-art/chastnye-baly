"""Сверка этапа 4 (05 Шоу, 06 Ассистент, 07 Уроки, 08 Этикет): кадры сайта под кадры Figma и пары «Figma | сайт».

  python tools/stage4_shots.py                  # все блоки → сверка/<блок>/
  python tools/stage4_shots.py --only show -b webkit

Покой — секция целиком на 390 / 834 / 1440 в окне её высоты (шапка скрыта, переходы мгновенные, reduced-motion:
десктоп 05 без закрепления — сцена 1180, как кадр). Состояния: 05 форматы 02 / 03 (пункт), 06 вопросы 02 / 03 (мышь),
08 «Дамам» (пункт). Середины смен (занавес 05, роль 08) — без reduced-motion, переходы на паузе на 50 %.
Рендеры Figma — _figma/v4/.
"""
import argparse
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from _serve import SVERKA, TOOLS, VERSTKA, serve, url_for

FIG = VERSTKA / "_figma" / "v4"
STILL = ("*,*::before,*::after{transition-duration:0s!important;transition-delay:0s!important;scroll-behavior:auto!important}"
         ".site-header,.skip{visibility:hidden!important}")
HEIGHTS = {390: 844, 834: 1194, 1440: 932}
PFX = {390: "m", 834: "t", 1440: "d"}


def page_at(browser, base, w, h=None, still=True, reduced=True):
    ctx = browser.new_context(viewport={"width": w, "height": h or HEIGHTS[w]}, reduced_motion="reduce" if reduced else "no-preference")
    page = ctx.new_page()
    page.goto(url_for(base, "site/index.html"), wait_until="networkidle")
    if still:
        page.add_style_tag(content=STILL)
    else:
        page.add_style_tag(content=".site-header,.skip{visibility:hidden!important}")
    page.evaluate("""async () => {
        document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager');
        await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
        await document.fonts.ready;
    }""")
    page.wait_for_timeout(150)
    return ctx, page


def pair(fig, site, out):
    if Path(fig).exists() and Path(site).exists():
        subprocess.run([sys.executable, str(TOOLS / "pair.py"), str(fig), str(site), "-o", str(out)], check=True)


def scroll_to(page, sel, dy=0):
    page.evaluate("([s, dy]) => { const e = document.querySelector(s); scrollTo({ top: e.getBoundingClientRect().top + scrollY + dy, behavior: 'instant' }); }", [sel, dy])
    page.wait_for_timeout(150)


def finish_entries(page, sel):
    """Входы секции — сразу в конец (кадр покоя)."""
    page.evaluate("s => document.getAnimations().forEach(a => { const t = a.effect && a.effect.target; if (t && document.querySelector(s).contains(t)) a.finish(); })", sel)
    page.wait_for_timeout(60)


def section_shot(page, sel, path, w):
    h = page.evaluate("s => document.querySelector(s).getBoundingClientRect().height", sel)
    page.set_viewport_size({"width": w, "height": int(h) + 2})
    page.wait_for_timeout(200)
    scroll_to(page, sel)
    page.wait_for_timeout(1500)
    finish_entries(page, sel)
    b = page.locator(sel).first.bounding_box()
    page.screenshot(path=str(path), clip={"x": 0, "y": b["y"], "width": w, "height": b["height"]})


def run_block(browser, base, name, sel, fig, out, actions=None):
    """actions: {суффикс: js-действие на странице} — состояния, снятые после покоя на тех же ширинах."""
    for w in (390, 834, 1440):
        ctx, page = page_at(browser, base, w)
        p = out / f"site_{w}.png"
        section_shot(page, sel, p, w)
        pair(FIG / f"v4_{PFX[w]}_{fig}.png", p, out / f"pair_{w}.png")
        for sfx, (js, figname) in (actions or {}).items():
            if (w == 1440) != sfx.startswith("d_"):
                continue
            page.evaluate(js)
            page.wait_for_timeout(250)
            b = page.locator(sel).first.bounding_box()
            p = out / f"site_{w}_{sfx}.png"
            page.screenshot(path=str(p), clip={"x": 0, "y": b["y"], "width": w, "height": b["height"]})
            pair(FIG / f"v4_{PFX[w]}_{fig}_{figname}.png", p, out / f"pair_{w}_{sfx}.png")
        ctx.close()


def mid_change(browser, base, w, sel, click_js, fig, out_path, pair_path, t_ms):
    """Смена на паузе: клик, затем все переходы секции — на t_ms."""
    ctx, page = page_at(browser, base, w, still=False, reduced=False)
    h = page.evaluate("s => document.querySelector(s).getBoundingClientRect().height", sel)
    page.set_viewport_size({"width": w, "height": int(h) + 2})
    scroll_to(page, sel)
    page.wait_for_timeout(1800)
    finish_entries(page, sel)
    page.evaluate(click_js)
    page.evaluate("([s, t]) => document.getAnimations().forEach(a => { const e = a.effect && a.effect.target; "
                  "if (e && document.querySelector(s).contains(e)) { a.pause(); a.currentTime = t; } })", [sel, t_ms])
    page.wait_for_timeout(80)
    b = page.locator(sel).first.bounding_box()
    page.screenshot(path=str(out_path), clip={"x": 0, "y": b["y"], "width": w, "height": b["height"]})
    pair(fig, out_path, pair_path)
    ctx.close()


def pinned(browser, base, out):
    """05 десктоп с закреплением: окно 1440 × 900, шаги 1–3 по прокрутке, кадр — экран."""
    ctx, page = page_at(browser, base, 1440, 900, still=True, reduced=False)
    for i in (1, 2, 3):
        y = page.evaluate("""i => { const t = document.querySelector('.show__track'), s = document.querySelector('.show__stage');
            const r = t.getBoundingClientRect(), top = parseFloat(getComputedStyle(s).top);
            return r.top + scrollY - top + (i - 1) / 2 * (r.height - s.offsetHeight) + 1; }""", i)
        page.evaluate("y => scrollTo({ top: y, behavior: 'instant' })", y)
        page.wait_for_timeout(400)
        finish_entries(page, ".s-show")
        page.screenshot(path=str(out / f"site_1440x900_pin{i}.png"))
    ctx.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    a = ap.parse_args()
    sfx = "" if a.browser == "chromium" else "_webkit"
    with serve() as base, sync_playwright() as pw:
        b = getattr(pw, a.browser).launch()

        if a.only in (None, "show"):
            out = SVERKA / f"05{sfx}"
            out.mkdir(parents=True, exist_ok=True)
            tab = "document.querySelectorAll('.show__tab')[{}].click()"
            run_block(b, base, "show", ".s-show", "show", out, {
                "f2": (tab.format(1), "2"), "f3": (tab.format(2), "3"),
                "d_f2": (tab.format(1), "2"), "d_f3": (tab.format(2), "3"),
            })
            for w in (390, 834):
                mid_change(b, base, w, ".s-show", tab.format(1), FIG / f"v4_{PFX[w]}_show_curtain50.png",
                           out / f"site_{w}_curtain50.png", out / f"pair_{w}_curtain50.png", 600)
            pinned(b, base, out)

        if a.only in (None, "asst"):
            out = SVERKA / f"06{sfx}"
            out.mkdir(parents=True, exist_ok=True)
            run_block(b, base, "asst", ".s-assistant", "asst", out, {
                "d_q2": ("document.querySelectorAll('.asst__item')[1].dispatchEvent(new FocusEvent('focusin', {bubbles: true}))", "2"),
                "d_q3": ("document.querySelectorAll('.asst__item')[2].dispatchEvent(new FocusEvent('focusin', {bubbles: true}))", "3"),
            })

        if a.only in (None, "less"):
            out = SVERKA / f"07{sfx}"
            out.mkdir(parents=True, exist_ok=True)
            run_block(b, base, "less", ".s-lessons", "less", out)

        if a.only in (None, "etq"):
            out = SVERKA / f"08{sfx}"
            out.mkdir(parents=True, exist_ok=True)
            btn = "document.querySelectorAll('.etq__btn')[1].click()"
            run_block(b, base, "etq", ".s-etiquette", "etq", out, {"dam": (btn, "2"), "d_dam": (btn, "2")})
            for w in (390, 834):
                mid_change(b, base, w, ".s-etiquette", btn, FIG / f"v4_{PFX[w]}_etq_kd50.png",
                           out / f"site_{w}_kd50.png", out / f"pair_{w}_kd50.png", 200)
        b.close()


if __name__ == "__main__":
    main()
