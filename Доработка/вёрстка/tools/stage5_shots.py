"""Сверка этапа 5 (09 Дресс-код, 10 Вечера, 11–подвал, лист формы): кадры сайта под кадры Figma и пары «Figma | сайт».

  python tools/stage5_shots.py                  # всё → сверка/09, 10, 11, форма
  python tools/stage5_shots.py --only eves -b webkit

Покой — секция целиком на 390 / 834 / 1440 в окне её высоты (шапка скрыта, переходы мгновенные, reduced-motion).
11–подвал — одной лентой от «О нас» до конца подвала (на 1440 кадры Figma 191:890 / 895 / 901 / 930 склеены в v5_d_end).
Состояния: 09 наведение на правило (десктоп), 10 «Кашемир» (пункт) на трёх ширинах, середина смены О→К на 50 % (телефон, планшет).
Лист формы — экран: пусто, ввод (значения из десктопа), ошибки, «отправлено»; на 1440 кадра Figma нет.
Рендеры Figma — _figma/v5/.
"""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve
from stage4_shots import FIG as _FIG4, PFX, finish_entries, mid_change, page_at, pair, scroll_to, section_shot  # noqa: F401
import stage4_shots

FIG = _FIG4.parent / "v5"
stage4_shots.FIG = FIG
HEIGHTS = {390: 844, 834: 1194, 1440: 932}


def run_block(browser, base, sel, fig, out, actions=None):
    for w in (390, 834, 1440):
        ctx, page = page_at(browser, base, w)
        p = out / f"site_{w}.png"
        section_shot(page, sel, p, w)
        pair(FIG / f"v5_{PFX[w]}_{fig}.png", p, out / f"pair_{w}.png")
        for sfx, (js, figname) in (actions or {}).items():
            if (w == 1440) != sfx.startswith("d_"):
                continue
            page.evaluate(js)
            page.wait_for_timeout(300)
            b = page.locator(sel).first.bounding_box()
            p = out / f"site_{w}_{sfx}.png"
            page.screenshot(path=str(p), clip={"x": 0, "y": b["y"], "width": w, "height": b["height"]})
            if figname:
                pair(FIG / f"v5_{PFX[w]}_{fig}_{figname}.png", p, out / f"pair_{w}_{sfx}.png")
        ctx.close()


def end_strip(browser, base, out):
    """11 О нас → подвал одной лентой."""
    for w in (390, 834, 1440):
        ctx, page = page_at(browser, base, w)
        top, bottom = page.evaluate("""() => { const a = document.querySelector('.s-about').getBoundingClientRect(),
            f = document.querySelector('.s-footer').getBoundingClientRect(); return [a.top + scrollY, f.bottom + scrollY]; }""")
        page.set_viewport_size({"width": w, "height": int(bottom - top) + 2})
        page.evaluate("y => scrollTo({ top: y, behavior: 'instant' })", top)
        page.wait_for_timeout(1500)
        for s in (".s-about", ".s-cta", ".s-contact", ".s-footer"):
            finish_entries(page, s)
        # Высота окна меняет hero и закрепления (svh) — координаты ленты заново. Конец страницы не прокручивается
        # до верха ленты — снимок всей страницы с вырезом в её координатах
        top, bottom = page.evaluate("""() => { const a = document.querySelector('.s-about').getBoundingClientRect(),
            f = document.querySelector('.s-footer').getBoundingClientRect(); return [a.top + scrollY, f.bottom + scrollY]; }""")
        p = out / f"site_{w}.png"
        page.screenshot(path=str(p), full_page=True, clip={"x": 0, "y": top, "width": w, "height": bottom - top})
        pair(FIG / f"v5_{PFX[w]}_end.png", p, out / f"pair_{w}.png")
        ctx.close()


def sheet(browser, base, out):
    """Лист формы: экран после открытия с поля «Как вас зовут»."""
    fill = """() => { const f = document.querySelector('#form form');
        f.elements.name.value = 'Анна'; f.elements.phone.value = '+7 916 …';
        f.elements.message.value = 'Юбилей родителей, около шестидесяти гостей, весной.';
        f.elements.message.dispatchEvent(new Event('input')); }"""
    for w in (390, 834, 1440):
        ctx, page = page_at(browser, base, w, HEIGHTS[w])
        scroll_to(page, ".s-contact")
        page.locator(".cp__field").first.click()
        page.wait_for_timeout(600)
        page.screenshot(path=str(out / f"site_{w}.png"))
        pair(FIG / f"v5_{PFX[w]}_form.png", out / f"site_{w}.png", out / f"pair_{w}.png")
        page.evaluate(fill)
        page.wait_for_timeout(100)
        page.screenshot(path=str(out / f"site_{w}_input.png"))
        pair(FIG / f"v5_{PFX[w]}_form_input.png", out / f"site_{w}_input.png", out / f"pair_{w}_input.png")
        page.evaluate("() => { const f = document.querySelector('#form form'); f.reset(); f.requestSubmit(); }")
        page.wait_for_timeout(200)
        page.screenshot(path=str(out / f"site_{w}_errors.png"))
        page.evaluate(fill)
        page.evaluate("() => { const f = document.querySelector('#form form'); f.elements.phone.value = '+7 916 123-45-67'; f.requestSubmit(); }")
        page.wait_for_timeout(1100)
        page.screenshot(path=str(out / f"site_{w}_done.png"))
        ctx.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    a = ap.parse_args()
    sfx = "" if a.browser == "chromium" else "_webkit"
    with serve() as base, sync_playwright() as pw:
        b = getattr(pw, a.browser).launch()

        if a.only in (None, "dress"):
            out = SVERKA / f"09{sfx}"
            out.mkdir(parents=True, exist_ok=True)
            hover = ("document.querySelectorAll('.dress__rule')[{}].dispatchEvent(new PointerEvent('pointerenter', {{pointerType: 'mouse'}}))")
            run_block(b, base, ".s-dress", "dress", out, {"d_h3": (hover.format(2), None), "d_h6": (hover.format(5), None)})

        if a.only in (None, "eves"):
            out = SVERKA / f"10{sfx}"
            out.mkdir(parents=True, exist_ok=True)
            tab = "document.querySelectorAll('.eves__tab')[1].click()"
            run_block(b, base, ".s-eves", "eves", out, {"k": (tab, "2"), "d_k": (tab, "2")})
            for w in (390, 834):
                mid_change(b, base, w, ".s-eves", tab, FIG / f"v5_{PFX[w]}_eves_ok50.png",
                           out / f"site_{w}_ok50.png", out / f"pair_{w}_ok50.png", 600)

        if a.only in (None, "end"):
            out = SVERKA / f"11{sfx}"
            out.mkdir(parents=True, exist_ok=True)
            end_strip(b, base, out)

        if a.only in (None, "form"):
            out = SVERKA / f"форма{sfx}"
            out.mkdir(parents=True, exist_ok=True)
            sheet(b, base, out)
        b.close()


if __name__ == "__main__":
    main()
