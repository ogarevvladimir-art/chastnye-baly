"""Проверка доработки Д1: П-01 (шапка и подвал), П-03 (закрытие меню), Р-2 (страховка JS), Р-3 (меню на низком окне),
Р-8 / Р-9 / Р-10 (modulepreload, inert, h1), Р-14 (счётчик 08, фокус листа, автосмена 10), 360 (ссылка Форматов, слово меню).

  python tools/d1_check.py            # chromium
  python tools/d1_check.py -b webkit

Печатает «ok / !!» по пунктам.
"""
import argparse

from playwright.sync_api import sync_playwright

from _serve import serve, url_for

results = []


def check(name, ok, info=""):
    results.append(bool(ok))
    print(("ok  " if ok else "!!  ") + name + (f" — {info}" if info else ""))


def open_page(b, base, w, h, reduced=False, route=None, wait=1200, until="load"):
    ctx = b.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce" if reduced else "no-preference")
    p = ctx.new_page()
    errors = []
    p.on("pageerror", lambda e: errors.append(str(e)))
    p.on("console", lambda m: m.type == "error" and errors.append(m.text))
    if route:
        route(p)
    p.add_init_script("history.scrollRestoration = 'manual'")
    p.goto(url_for(base, "site/index.html"), wait_until=until)
    p.wait_for_timeout(wait)
    p.errors = errors
    return ctx, p


def to(p, sel, dy=0):
    p.evaluate("""([s, dy]) => { const r = document.querySelector(s).getBoundingClientRect();
        scrollTo({ top: r.top + scrollY + dy, behavior: 'instant' }); }""", [sel, dy])


def patch(p, name, fn):
    """Подменить модуль js/<name>: fn(text) → новый текст."""
    def handler(route):
        r = route.fetch()
        route.fulfill(response=r, body=fn(r.text()), headers={**r.headers, "cache-control": "no-store"})
    p.route(f"**/js/{name}", handler)


HIDDEN = """() => [...document.querySelectorAll('[data-reveal], [data-giant]')].filter(el => {
    const r = el.getBoundingClientRect(); return r.top < innerHeight * 0.85 && r.bottom > 0 && r.width > 0 && r.height > 0 && getComputedStyle(el).opacity === '0';
}).length"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    args = ap.parse_args()
    with serve() as base, sync_playwright() as pw:
        b = getattr(pw, args.browser).launch()

        # --- П-01, Р-8, Р-10: разметка ---
        ctx, p = open_page(b, base, 1440, 900)
        st = p.evaluate("""() => ({ nav: document.querySelectorAll('.site-header__nav, .site-header__phone, .footer__nav').length,
            header: [...document.querySelector('.site-header__in').children].map(c => c.className.baseVal ?? c.className),
            footer: document.querySelectorAll('.s-footer a').length,
            preload: document.querySelectorAll('link[rel=modulepreload]').length,
            first: document.querySelector('h1, h2').tagName,
            modal: document.getElementById('menu').hasAttribute('aria-modal') })""")
        check("П-01: в шапке только логотип и «Меню», в подвале одна ссылка (логотип)",
              st["nav"] == 0 and st["header"] == ["site-header__logo", "site-header__menu"] and st["footer"] == 1, str(st))
        check("Р-8: modulepreload у всех девяти модулей", st["preload"] == 9, str(st["preload"]))
        check("Р-10: первый заголовок страницы — h1", st["first"] == "H1", st["first"])
        check("Р-9: у меню нет aria-modal", not st["modal"])
        check("без ошибок JS", not p.errors, "; ".join(p.errors))
        ctx.close()

        # --- П-03, Р-9: закрытие меню на десктопе ---
        ctx, p = open_page(b, base, 1440, 932)
        p.click(".site-header__menu")
        p.wait_for_timeout(900)
        st = p.evaluate("() => [document.querySelector('main').inert, document.querySelector('footer').inert, document.querySelector('.skip').inert]")
        check("Р-9: при открытом меню main, подвал и «К содержанию» — inert", st == [True, True, True], str(st))
        p.hover('.menu__item[href="#etiquette"]')
        p.wait_for_timeout(400)
        p.click(".site-header__menu")
        p.wait_for_timeout(120)
        op = p.evaluate("[...document.querySelectorAll('.menu__word')].map(w => +getComputedStyle(w).opacity)")
        check("П-03: «Закрыть» — гигантов не видно во время закрытия", max(op) == 0, str(op))
        p.wait_for_timeout(900)
        st = p.evaluate("() => [document.querySelector('main').inert, document.querySelector('footer').inert]")
        check("Р-9: после закрытия inert снят", st == [False, False], str(st))

        p.click(".site-header__menu")
        p.wait_for_timeout(900)
        p.hover('.menu__item[href="#lessons"]')
        p.wait_for_timeout(400)
        y0 = p.evaluate("""document.querySelector('.menu__item[href="#lessons"] .menu__word').getBoundingClientRect().top""")
        p.click('.menu__item[href="#lessons"]')
        p.wait_for_timeout(150)
        st = p.evaluate("""() => { const ws = [...document.querySelectorAll('.menu__item')].map(a => [a.getAttribute('href'),
            +getComputedStyle(a.querySelector('.menu__word')).opacity, a.querySelector('.menu__word').getBoundingClientRect().top]);
            return { on: ws.filter(w => w[1] > 0).map(w => w[0]), top: ws.find(w => w[0] === '#lessons')[2] }; }""")
        p.wait_for_timeout(300)
        y2 = p.evaluate("""document.querySelector('.menu__item[href="#lessons"] .menu__word').getBoundingClientRect().top""")
        check("П-03: клик по пункту — виден только его гигант", st["on"] == ["#lessons"], str(st["on"]))
        check("П-03: гигант пункта уезжает вверх со шторкой", y0 > st["top"] > y2, f"{y0:.0f} → {st['top']:.0f} → {y2:.0f}")
        p.wait_for_timeout(1200)
        top = p.evaluate("Math.round(document.querySelector('#lessons').getBoundingClientRect().top)")
        check("П-03: пункт привёл к разделу", p.evaluate("menu.dataset.state") == "closed" and abs(top) <= 80, f"top {top}")
        ctx.close()

        # Телефон: при закрытии слова по-прежнему уезжают со шторкой (видимы)
        ctx, p = open_page(b, base, 390, 844)
        p.click(".site-header__menu")
        p.wait_for_timeout(900)
        p.click(".site-header__menu")
        p.wait_for_timeout(120)
        op = p.evaluate("[...document.querySelectorAll('.menu__word')].map(w => +getComputedStyle(w).opacity)")
        check("П-03: телефон — при закрытии все слова видимы (уезжают со шторкой)", min(op) == 1, str(op))
        ctx.close()

        # --- Р-3: меню на низких окнах — гигант не заходит на метки и контакты ---
        for w, h in ((1440, 932), (1920, 950), (1366, 650), (1280, 600), (1024, 600)):
            ctx, p = open_page(b, base, w, h, wait=300)
            p.click(".site-header__menu")
            p.wait_for_timeout(900)
            bad = []
            fs = set()
            for href in p.evaluate("[...document.querySelectorAll('.menu__item')].map(a => a.getAttribute('href'))"):
                p.hover(f'.menu__item[href="{href}"]')
                p.wait_for_timeout(320)
                r = p.evaluate("""(href) => {
                    const box = (el) => el.getBoundingClientRect();
                    const word = box(document.querySelector(`.menu__item[href="${href}"] .menu__word`));
                    const hit = (a, b) => a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
                    const labels = [...document.querySelectorAll('.menu__label')].filter(l => hit(word, box(l))).length;
                    // контакты — по тексту (у ссылки зона нажатия 44 выше и ниже строки)
                    const text = (el) => { const r = document.createRange(); r.selectNodeContents(el); return r.getBoundingClientRect(); };
                    const contacts = [...document.querySelectorAll('.menu__contacts a')].filter(c => hit(word, text(c))).length;
                    return { labels, contacts, fs: getComputedStyle(document.querySelector('.menu__word')).fontSize };
                }""", href)
                fs.add(r["fs"])
                if r["labels"] or r["contacts"]:
                    bad.append(f"{href} метки {r['labels']} контакты {r['contacts']}")
            check(f"Р-3: меню {w}×{h} — гигант не заходит на метки и контакты (кегль {', '.join(fs)})", not bad, str(bad))
            ctx.close()

        # --- Р-14: счётчик 08, фокус листа, автосмена 10 ---
        ctx, p = open_page(b, base, 390, 844)
        to(p, ".s-etiquette", 0)
        p.wait_for_timeout(600)
        n0 = p.evaluate("document.querySelector('.etq__count-n').textContent")
        p.locator(".etq__btn").nth(1).click()
        p.wait_for_timeout(600)
        n1 = p.evaluate("document.querySelector('.etq__count-n').textContent")
        total = p.evaluate("document.querySelector('.etq__count').textContent.trim()")
        check("Р-14: счётчик 08 — «01 / 02» → «02 / 02»", n0 == "01" and n1 == "02" and total.endswith("02 / 02"), f"{n0} → {n1}, «{total}»")
        to(p, ".s-hero", 0)
        p.locator(".s-hero__link").click()
        p.wait_for_timeout(600)
        st = p.evaluate("() => [document.activeElement.id, getComputedStyle(document.activeElement).outlineStyle]")
        check("Р-14: «→ обсудить вечер» — фокус на заголовке листа (без клавиатуры), без рамки", st == ["form-h", "none"], str(st))
        p.keyboard.press("Escape")
        p.wait_for_timeout(600)
        p.locator(".fmt__link").nth(0).click()
        p.wait_for_timeout(600)
        check("Р-14: «Обсудить частный бал →» — фокус на заголовке листа", p.evaluate("document.activeElement.id") == "form-h")
        p.keyboard.press("Escape")
        p.wait_for_timeout(600)
        to(p, ".contact__panel", -300)
        p.wait_for_timeout(1200)
        p.locator(".cp__field").nth(0).click()
        p.wait_for_timeout(600)
        check("Р-14: тап по полю панели — фокус в поле", p.evaluate("document.activeElement.id") == "f-name")
        ctx.close()

        ctx, p = open_page(b, base, 1440, 900)
        to(p, ".eves__body", -100)
        p.mouse.move(5, 5)
        p.wait_for_timeout(4700)
        auto = p.evaluate("document.querySelector('.s-eves').dataset.step")
        p.wait_for_timeout(1300)                        # смена (1,2 с) доиграла — клик принимается
        p.locator(".eves__tab").nth(0).click()
        p.wait_for_timeout(1400)
        p.mouse.move(5, 5)
        p.evaluate("document.activeElement.blur()")
        p.wait_for_timeout(5000)
        st = p.evaluate("document.querySelector('.s-eves').dataset.step")
        check("Р-14: автосмена 10 идёт до выбора и останавливается после клика", auto == "2" and st == "1", f"авто → {auto}, после клика → {st}")
        ctx.close()

        # --- Р-2: страховка JS ---
        # Ошибка в одном блоке (10): остальные работают, текст виден
        ctx, p = open_page(b, base, 390, 844, route=lambda p: patch(p, "blocks.js",
                           lambda t: t.replace("function initEvenings() {", "function initEvenings() { throw new Error('тест Р-2');")))
        st = p.evaluate("() => ({ js: document.documentElement.className, motion: window.__motion })")
        to(p, ".s-etiquette", 0)
        p.wait_for_timeout(1200)
        hidden = p.evaluate(HIDDEN)
        p.locator(".etq__btn").nth(1).click()
        p.wait_for_timeout(600)
        role = p.evaluate("document.querySelector('.s-etiquette').dataset.role")
        p.click(".site-header__menu")
        p.wait_for_timeout(900)
        menu = p.evaluate("menu.dataset.state")
        check("Р-2: ошибка в блоке 10 — входы работают, 08 и меню работают",
              st["motion"] and "no-motion" not in st["js"] and hidden == 0 and role == "d" and menu == "open" and p.errors,
              f"{st}, скрыто {hidden}, 08 {role}, меню {menu}, ошибки {len(p.errors)}")
        ctx.close()

        # Ошибка в motion.js (входы не запустились): no-motion сразу, всё видно, меню работает
        ctx, p = open_page(b, base, 390, 844, route=lambda p: patch(p, "motion.js",
                           lambda t: t.replace("const giants = els.filter", "throw new Error('тест Р-2'); const giants = els.filter")))
        st = p.evaluate("() => ({ cls: document.documentElement.className, motion: !!window.__motion })")
        to(p, ".s-prep", 0)
        p.wait_for_timeout(300)
        hidden = p.evaluate(HIDDEN)
        p.click(".site-header__menu")
        p.wait_for_timeout(900)
        check("Р-2: ошибка во входах — no-motion, текст виден, меню работает",
              "no-motion" in st["cls"] and not st["motion"] and hidden == 0 and p.evaluate("menu.dataset.state") == "open", f"{st}, скрыто {hidden}")
        ctx.close()

        # Модули не загрузились (404 главного модуля): сразу режим «без JS» — форма на странице, панели нет, описания открыты
        ctx, p = open_page(b, base, 390, 844, wait=300, route=lambda p: p.route("**/js/main.js", lambda r: r.fulfill(status=404, body="")))
        st = p.evaluate("""() => ({ js: document.documentElement.classList.contains('js'),
            sheet: getComputedStyle(document.getElementById('form')).display,
            panel: getComputedStyle(document.querySelector('.contact__panel')).display })""")
        to(p, ".s-prep", 0)
        hidden = p.evaluate(HIDDEN)
        check("Р-2: модули не загрузились — сразу без JS: класс js снят, лист на странице, панели нет, текст виден",
              st == {"js": False, "sheet": "block", "panel": "none"} and hidden == 0, f"{st}, скрыто {hidden}")
        ctx.close()

        # Синтаксическая ошибка в модуле: граф не выполняется — через 3 с режим «без JS»
        ctx, p = open_page(b, base, 1440, 900, wait=200, route=lambda p: patch(p, "switch.js", lambda t: t + "\nexport function {"))
        early = p.evaluate("document.documentElement.classList.contains('js')")
        p.wait_for_timeout(3200)
        st = p.evaluate("() => [document.documentElement.classList.contains('js'), getComputedStyle(document.getElementById('form')).display]")
        to(p, ".s-prep", 0)
        hidden = p.evaluate(HIDDEN)
        check("Р-2: синтаксическая ошибка в модуле — через 3 с без JS, текст виден", st == [False, "block"] and hidden == 0,
              f"сначала js {early}, потом {st}, скрыто {hidden}")
        ctx.close()

        # Модули пришли позже страховки (4 с): js возвращается без анимаций входа, меню и форма работают
        held = []
        ctx, p = open_page(b, base, 390, 844, wait=3300, until="commit", route=lambda p: p.route("**/js/main.js", lambda r: held.append(r)))
        before = p.evaluate("document.documentElement.className")
        for r in held:
            r.continue_()
        p.wait_for_function("window.__ready === true", timeout=15000)
        p.wait_for_timeout(500)
        after = p.evaluate("document.documentElement.className")
        to(p, ".s-prep", 0)
        p.wait_for_timeout(300)
        hidden = p.evaluate(HIDDEN)
        p.click(".site-header__menu")
        p.wait_for_timeout(900)
        menu = p.evaluate("menu.dataset.state")
        check("Р-2: модули опоздали — сначала без JS, затем js + no-motion, текст виден, меню работает",
              "js" not in before.split() and {"js", "no-motion"} <= set(after.split()) and hidden == 0 and menu == "open",
              f"«{before}» → «{after}», скрыто {hidden}, меню {menu}")
        ctx.close()

        # --- 360: «Обсудить корпоративный бал →» и «ПОДГОТОВКА» в меню — в колонке ---
        ctx, p = open_page(b, base, 360, 780)
        r = p.evaluate("() => [...document.querySelectorAll('.fmt__link')].map(a => Math.ceil(a.getBoundingClientRect().right))")
        check("360: ссылки Форматов не заходят в правое поле (≤ 344)", max(r) <= 344, str(r))
        p.click(".site-header__menu")
        p.wait_for_timeout(900)
        r = p.evaluate("Math.max(...[...document.querySelectorAll('.menu__word')].map(w => w.getBoundingClientRect().right))")
        check("360: слова меню в колонке (≤ 344)", r <= 344, f"{r:.1f}")
        ctx.close()
        b.close()
    print(f"\n{sum(results)} / {len(results)} ok")


if __name__ == "__main__":
    main()
