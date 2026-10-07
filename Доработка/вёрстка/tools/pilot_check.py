"""Проверка поведения пилота (этап 2): меню, клавиатура, блокировка скролла, якоря, шапка «Над светлым», вертикальный гигант.

  python tools/pilot_check.py            # chromium
  python tools/pilot_check.py -b webkit

Печатает «ok / !!» по пунктам; кадры вертикального гиганта → сверка/hero/v2_vgiant_*.png
"""
import argparse

from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve, url_for

results = []


def check(name, ok, info=""):
    results.append(ok)
    print(("ok  " if ok else "!!  ") + name + (f" — {info}" if info else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    args = ap.parse_args()
    with serve() as base, sync_playwright() as pw:
        b = getattr(pw, args.browser).launch()

        # --- Меню на телефоне ---
        ctx = b.new_context(viewport={"width": 390, "height": 844})
        p = ctx.new_page()
        p.goto(url_for(base, "site/index.html"), wait_until="networkidle")
        p.wait_for_timeout(1600)
        p.evaluate("scrollTo(0, 500)")
        p.wait_for_timeout(100)
        vw_before = p.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--vw')")
        p.click(".site-header__menu")
        p.wait_for_timeout(900)
        st = p.evaluate("""() => ({state: menu.dataset.state, inert: menu.inert, expanded: document.querySelector('.site-header__menu').getAttribute('aria-expanded'),
            label: document.querySelector('.site-header__menu-text').textContent, locked: document.documentElement.classList.contains('is-locked'),
            y: scrollY, focus: document.activeElement.getAttribute('aria-label'), vw: getComputedStyle(document.documentElement).getPropertyValue('--vw')})""")
        check("меню открылось", st["state"] == "open" and not st["inert"] and st["expanded"] == "true", str(st))
        check("«Меню» → «Закрыть»", st["label"] == "Закрыть", st["label"])
        check("скролл заблокирован без прыжка", st["locked"] and st["y"] == 500, f"scrollY {st['y']}")
        check("ширина окна не прыгнула (--vw)", st["vw"] == vw_before, f"{vw_before} → {st['vw']}")
        check("фокус на первом пункте", st["focus"] == "Подготовка", str(st["focus"]))
        p.mouse.wheel(0, 400)
        p.wait_for_timeout(200)
        check("колесо не крутит страницу под меню", p.evaluate("scrollY") == 500)
        # Tab по кругу: 1 кнопка + 2 контакта + 12 пунктов
        p.keyboard.press("Shift+Tab")
        check("Shift+Tab с первого пункта → почта", p.evaluate("document.activeElement.textContent") == "hello@ballevent.ru")
        for _ in range(3):
            p.keyboard.press("Shift+Tab")
        check("…→ кнопка → последний пункт (кольцо)", p.evaluate("document.activeElement.getAttribute('aria-label')") == "Связаться")
        p.keyboard.press("Tab")
        check("Tab с последнего → кнопка", p.evaluate("document.activeElement.classList.contains('site-header__menu')"))
        p.keyboard.press("Escape")
        p.wait_for_timeout(900)
        st = p.evaluate("""() => ({state: menu.dataset.state, inert: menu.inert, label: document.querySelector('.site-header__menu-text').textContent,
            locked: document.documentElement.classList.contains('is-locked'), focus: document.activeElement.classList.contains('site-header__menu'), y: scrollY})""")
        check("Esc закрывает, фокус на кнопке", st["state"] == "closed" and st["inert"] and st["focus"] and not st["locked"], str(st))
        check("«Закрыть» → «Меню»", st["label"] == "Меню")
        # Пункт ведёт к якорю
        p.click(".site-header__menu")
        p.wait_for_timeout(900)
        p.click('.menu__item[href="#music"]')
        p.wait_for_timeout(1500)
        top = p.evaluate("Math.round(document.querySelector('#music').getBoundingClientRect().top)")
        check("пункт «Музыка» закрыл меню и привёл к #music под шапку", p.evaluate("menu.dataset.state") == "closed" and abs(top - 64) <= 2,
              f"top {top}, hash {p.evaluate('location.hash')}")
        ctx.close()

        # --- Десктоп: наведение меню, Esc, наведение половин и слово у шва ---
        ctx = b.new_context(viewport={"width": 1440, "height": 932})
        p = ctx.new_page()
        p.goto(url_for(base, "site/index.html"), wait_until="networkidle")
        p.wait_for_timeout(1600)
        p.click(".site-header__menu")
        p.wait_for_timeout(900)
        p.hover('.menu__item[href="#etiquette"]')
        p.wait_for_timeout(400)
        op = p.evaluate("""getComputedStyle(document.querySelector('.menu__item[href="#etiquette"] .menu__word')).opacity""")
        check("десктоп: наведение на 08 показывает гигант", op == "1", op)
        parts = p.evaluate("[...document.querySelector('.site-header__in').children].map(c => c.className)")
        check("десктоп: в шапке только логотип и «Меню» (П-01)", parts == ["site-header__logo", "site-header__menu"], str(parts))
        p.keyboard.press("Escape")
        p.wait_for_timeout(900)
        p.mouse.move(700, 100)
        top = p.evaluate("document.querySelector('#formats').getBoundingClientRect().top + scrollY")
        p.evaluate("y => scrollTo(0, y)", top)
        p.wait_for_timeout(300)
        docked = p.evaluate("document.querySelector('.hf').hasAttribute('data-docked')")
        check("десктоп: слово у шва (data-docked) в Форматах", docked)
        p.mouse.move(300, 600)
        p.wait_for_timeout(500)
        st = p.evaluate("""() => ({s: document.querySelector('.s-formats').dataset.state,
            word: getComputedStyle(document.querySelector('.hf__giant-in')).transform})""")
        check("десктоп: наведение «частные» → state private, слово опустилось", st["s"] == "private" and st["word"] != "none", str(st))
        p.mouse.move(1300, 600)
        p.wait_for_timeout(500)
        check("десктоп: переход на «корпоративные»", p.evaluate("document.querySelector('.s-formats').dataset.state") == "corporate")
        p.mouse.move(700, 960 + 300)
        p.evaluate("scrollBy(0, 400)")
        p.wait_for_timeout(500)
        p.mouse.move(700, 900)
        p.wait_for_timeout(300)
        # фокус клавиатурой на ссылке половины
        p.evaluate("document.querySelector('[data-half=private] .fmt__link').focus()")
        p.wait_for_timeout(400)
        st = p.evaluate("""() => [document.querySelector('.s-formats').dataset.state, getComputedStyle(document.querySelector('[data-half=private] .fmt__link')).opacity]""")
        check("десктоп: фокус на ссылке раскрывает половину", st == ["private", "1"], str(st))
        ctx.close()

        # --- Шапка «Над светлым» и вертикальный гигант (тестовая страница) ---
        ctx = b.new_context(viewport={"width": 390, "height": 844})
        p = ctx.new_page()
        p.goto(url_for(base, "Доработка/вёрстка/tools/motion-test.html"), wait_until="networkidle")
        vy = p.evaluate("document.querySelector('#v').getBoundingClientRect().top + scrollY")
        p.evaluate("y => scrollTo({top: y - 300, behavior: 'instant'})", vy)
        p.wait_for_function("document.getAnimations().length > 0")
        for pct, t in ((0, 0), (25, 400), (100, 1300)):
            p.evaluate("t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t; })", t)
            p.wait_for_timeout(50)
            p.locator("#v").screenshot(path=str(SVERKA / "hero" / f"v2_vgiant_{pct}.png"))
        y = p.evaluate("document.querySelector('#light').getBoundingClientRect().top + scrollY")
        p.evaluate("y => scrollTo({top: y - 10, behavior: 'instant'})", y)
        p.wait_for_timeout(400)
        v1 = p.evaluate("document.querySelector('.site-header').dataset.variant")
        p.evaluate("y => scrollTo({top: y - 60, behavior: 'instant'})", y)
        p.wait_for_timeout(400)
        v2 = p.evaluate("document.querySelector('.site-header').dataset.variant")
        check("шапка: над светлой секцией light, выше — dark", v1 == "light" and v2 == "dark", f"{v1} / {v2}")
        sw = p.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        check("вертикальный гигант: без горизонтального скролла", sw <= 0, f"{sw}px")
        ctx.close()

        # --- Д2 «в экран»: hero и Форматы ровно в окно; в наведении описание и «Обсудить … →» видны вместе,
        #     «БАЛЫ» не заходят на описание и название; телефон и планшет — без изменений ---
        for w, h in ((1440, 900), (1920, 950), (1366, 650), (1024, 650)):
            ctx = b.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
            p = ctx.new_page()
            p.goto(url_for(base, "site/index.html"), wait_until="networkidle")
            p.wait_for_timeout(400)
            hh = p.evaluate("[document.querySelector('.s-hero').offsetHeight, document.querySelector('#formats').offsetHeight]")
            check(f"Д2 {w}×{h}: hero и Форматы = окно", hh == [h, h], str(hh))
            top = p.evaluate("document.querySelector('#formats').getBoundingClientRect().top + scrollY")
            p.evaluate("y => scrollTo({top: y, behavior: 'instant'})", top)
            p.wait_for_timeout(200)
            for half, fx in (("private", 0.15), ("corporate", 0.9)):
                p.mouse.move(w * fx, h * 0.7)
                p.wait_for_timeout(450)
                r = p.evaluate("""half => {
                    const P = `[data-half=${half}] `, q = (s) => document.querySelector(s).getBoundingClientRect();
                    const d = q(P + '.fmt__desc'), l = q(P + '.fmt__link'), t = q(P + '.fmt__title'), g = q('.hf__giant-in');
                    const fs = parseFloat(getComputedStyle(document.querySelector('.hf__giant-in')).fontSize);
                    return {state: document.querySelector('#formats').dataset.state, descTop: d.top, linkBottom: l.bottom,
                            gap: g.top + 0.05 * fs - d.bottom, title: [t.bottom, g.top + 0.05 * fs],
                            sw: document.documentElement.scrollWidth - document.documentElement.clientWidth}; }""", half)
                ok = r["state"] == half and r["descTop"] >= 72 and r["linkBottom"] <= h and r["gap"] >= 23 and r["title"][0] <= r["title"][1] + 1 and r["sw"] <= 0
                check(f"Д2 {w}×{h}: наведение «{half}» — описание и ссылка в окне, слово ниже описания", ok,
                      f"desc {r['descTop']:.0f}, link ↓{r['linkBottom']:.0f}, зазор {r['gap']:.0f}, название ↓{r['title'][0]:.0f} / буквы {r['title'][1]:.0f}, sw {r['sw']}")
            ctx.close()
        for w, h in ((390, 844), (834, 1194)):
            ctx = b.new_context(viewport={"width": w, "height": h})
            p = ctx.new_page()
            p.goto(url_for(base, "site/index.html"), wait_until="networkidle")
            fh = p.evaluate("document.querySelector('#formats').offsetHeight")
            check(f"Д2 {w}: Форматы — поток, не в экран", fh > h, f"{fh}px")
            ctx.close()
        b.close()
    print(f"\n{sum(results)} / {len(results)} ok")


if __name__ == "__main__":
    main()
