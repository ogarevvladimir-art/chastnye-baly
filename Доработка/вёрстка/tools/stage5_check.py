"""Проверка поведения этапа 5: 09 Дресс-код, 10 Вечера, 11–подвал, лист формы, шапка над панелью формы, без JS.

  python tools/stage5_check.py            # chromium
  python tools/stage5_check.py -b webkit

Печатает «ok / !!» по пунктам.
"""
import argparse

from playwright.sync_api import sync_playwright

from _serve import WIDTHS, serve, url_for
from stage4_check import check, open_page, results, to, touch_swipe


def rules_overlap(p):
    """Пары правил одной фигуры, которые наезжают друг на друга (планшет и десктоп)."""
    return p.evaluate("""() => { const bad = [];
        document.querySelectorAll('.dress__fig').forEach(f => {
            const r = [...f.querySelectorAll('.dress__rule')].map(e => e.getBoundingClientRect());
            for (let i = 1; i < r.length; i++) if (r[i].top < r[i - 1].bottom - 0.5) bad.push(f.dataset.fig + i);
        }); return bad; }""")


def eves(p):
    return p.evaluate("""() => { const s = document.querySelector('.s-eves');
        const act = [...s.querySelectorAll('.eves__panel')].find(x => x.dataset.pos === 'active');
        return { step: s.dataset.step, panel: act && act.dataset.i, count: s.querySelector('.eves__count-n').textContent,
                 sel: [...s.querySelectorAll('.eves__tab')].findIndex(b => b.getAttribute('aria-selected') === 'true') + 1 }; }""")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    a = ap.parse_args()
    with serve() as base, sync_playwright() as pw:
        b = getattr(pw, a.browser).launch()

        # --- Горизонтальный скролл: секции 09–подвал, в том числе во время входов ---
        bad = []
        for w in WIDTHS:
            ctx, p = open_page(b, base, w, 900)
            worst = 0
            for sel in (".s-dress", ".dress__fig[data-fig='d']", ".dress__white", ".s-eves", ".eves__scene", ".eves__info", ".s-about", ".s-contact", ".s-footer"):
                to(p, sel, -200)
                p.wait_for_timeout(250)
                worst = max(worst, p.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth"))
            if worst > 0:
                bad.append(f"{w}: {worst}px")
            ctx.close()
        check("горизонтального скролла нет на " + ", ".join(map(str, WIDTHS)), not bad, "; ".join(bad))

        # --- 09: правила не наезжают, «+» внутри фото ---
        over = {}
        for w in (600, 700, 834, 1023, 1024, 1280, 1440, 1920):
            ctx, p = open_page(b, base, w, 900, reduced=True)
            o = rules_overlap(p)
            if o:
                over[w] = o
            ctx.close()
        check("09: правила планшета и десктопа не наезжают (600…1920)", not over, str(over))

        ctx, p = open_page(b, base, 834, 1194, reduced=True)
        r = p.evaluate("""() => [...document.querySelectorAll('.dress__fig')].map(f => {
            const ph = f.querySelector('.dress__photo').getBoundingClientRect();
            return [...f.querySelectorAll('.dress__plus')].every(x => { const b = x.getBoundingClientRect(), cx = b.left + 9, cy = b.top + 9;
                return cx > ph.left && cx < ph.right && cy > ph.top && cy < ph.bottom; }); })""")
        check("09: «+» на фото (планшет)", all(r), str(r))
        # Центр правила на высоте своего «+» (планшет)
        d = p.evaluate("""() => { const f = document.querySelector('.dress__fig[data-fig="k"]');
            const pl = [...f.querySelectorAll('.dress__plus')], ru = [...f.querySelectorAll('.dress__rule')];
            return Math.max(...ru.map((x, i) => { const a = x.getBoundingClientRect(), b = pl[i].getBoundingClientRect();
                return Math.abs((a.top + a.bottom) / 2 - (b.top + b.bottom) / 2); })); }""")
        check("09: правило на высоте своего «+» (планшет)", d < 6, f"{d:.1f}px")
        ctx.close()

        ctx, p = open_page(b, base, 1440, 932)
        to(p, ".dress__fig", -200)
        p.wait_for_timeout(2500)
        p.locator(".dress__rule").nth(2).hover()
        p.wait_for_timeout(400)
        st = p.evaluate("""() => { const f = document.querySelector('.dress__fig'), r = [...f.querySelectorAll('.dress__rule')], x = [...f.querySelectorAll('.dress__plus')];
            return { hl: f.dataset.hl, op: r.map(e => +getComputedStyle(e).opacity), rot: getComputedStyle(x[2]).transform }; }""")
        check("09: наведение — «+» повёрнут, остальные правила 40 %",
              st["hl"] == "3" and st["op"][2] == 1 and all(abs(o - 0.4) < 0.01 for i, o in enumerate(st["op"]) if i != 2) and st["rot"] != "none", str(st))
        p.mouse.move(5, 5)
        p.wait_for_timeout(400)
        check("09: уход курсора — покой", p.evaluate("!document.querySelector('.dress__fig').dataset.hl"))
        ctx.close()

        # --- 10: телефон — тап, счётчик, линия, свайп, повторный тап во время смены ---
        ctx, p = open_page(b, base, 390, 844, touch=True)
        to(p, ".eves__win", -300)
        p.wait_for_timeout(1800)
        to(p, ".s-eves")
        y1 = p.evaluate("getComputedStyle(document.querySelector('.eves__mark')).transform")
        p.locator(".eves__tab").nth(1).click()
        p.wait_for_timeout(300)
        e = eves(p)
        y2 = p.evaluate("getComputedStyle(document.querySelector('.eves__mark')).transform")
        check("10: тап по пункту — Кашемир, счётчик 02, линия переехала", e == {"step": "2", "panel": "2", "count": "02", "sel": 2} and y1 != y2, f"{e}")
        p.locator(".eves__tab").nth(0).click()
        p.wait_for_timeout(100)
        check("10: тап во время смены (1,2 с) не принимается", eves(p)["step"] == "2")
        p.wait_for_timeout(1300)
        clip = p.evaluate("""() => { const f = [...document.querySelectorAll('.eves__slot[data-slot="b"] .eves__frame')];
            return f.map(x => x.dataset.pos + ':' + getComputedStyle(x).clipPath); }""")
        check("10: занавес — Кашемир открыт, Омега под ним", clip[1].startswith("active") and "50%" not in clip[1] and clip[0].startswith("before"), str(clip))
        touch_swipe(p, ".eves__slot[data-slot='b']", -120)
        p.wait_for_timeout(200)
        check("10: свайп влево — следующий по кругу (Омега)", eves(p)["step"] == "1")
        p.wait_for_timeout(1300)
        touch_swipe(p, ".eves__slot[data-slot='b']", 20)
        check("10: короткий жест не переключает", eves(p)["step"] == "1")
        touch_swipe(p, ".eves__slot[data-slot='b']", 120)
        p.wait_for_timeout(200)
        check("10: свайп вправо — предыдущий", eves(p)["step"] == "2")
        p.wait_for_timeout(5000)
        check("10: на телефоне автосмены нет", eves(p)["step"] == "2")
        giants = p.evaluate("""() => [...document.querySelectorAll('.eves__word')].map(w => [...w.querySelectorAll('[data-giant]')].every(g => 'in' in g.dataset))""")
        check("10: слова обоих вечеров в покое после входа", all(giants), str(giants))
        ctx.close()

        # --- 10: десктоп — автосмена 4 с, пауза при наведении, reduced-motion ---
        ctx, p = open_page(b, base, 1440, 932)
        to(p, ".eves__body", -100)
        p.wait_for_timeout(4600)
        check("10: десктоп — автосмена через 4 с", eves(p)["step"] == "2", str(eves(p)))
        p.mouse.move(700, 400)
        p.wait_for_timeout(5000)
        check("10: пауза при наведении на сцену", eves(p)["step"] == "2")
        p.mouse.move(700, 5)
        to(p, ".s-dress")
        p.wait_for_timeout(5000)
        check("10: вне экрана автосмены нет", eves(p)["step"] == "2")
        to(p, ".eves__body", -100)
        p.locator(".eves__tab").nth(0).click()
        p.wait_for_timeout(300)
        check("10: клик по пункту", eves(p)["step"] == "1")
        ctx.close()

        ctx, p = open_page(b, base, 1440, 932, reduced=True)
        to(p, ".eves__body", -100)
        p.wait_for_timeout(4600)
        check("10: reduced-motion — без автосмены", eves(p)["step"] == "1")
        p.locator(".eves__tab").nth(1).click()
        p.wait_for_timeout(300)
        op = p.evaluate("[...document.querySelectorAll('.eves__slot[data-slot=\"b\"] .eves__frame')].map(f => getComputedStyle(f).opacity)")
        check("10: reduced-motion — смена растворением", op == ["0", "1"], str(op))
        ctx.close()

        # --- Лист формы ---
        ctx, p = open_page(b, base, 390, 844)
        p.locator(".s-hero__link").click()
        p.wait_for_timeout(600)
        st = p.evaluate("""() => { const d = document.getElementById('form');
            return { open: d.open, state: d.dataset.state, lock: document.documentElement.classList.contains('is-locked'),
                     focus: document.activeElement.id, op: getComputedStyle(d).opacity }; }""")
        check("форма: «→ обсудить вечер» открывает лист, фокус на заголовке листа (Р-14), скролл заблокирован",
              st == {"open": True, "state": "open", "lock": True, "focus": "form-h", "op": "1"}, str(st))
        p.keyboard.press("Escape")
        p.wait_for_timeout(600)
        st = p.evaluate("() => ({ open: document.getElementById('form').open, lock: document.documentElement.classList.contains('is-locked'), f: document.activeElement.className })")
        check("форма: Esc закрывает, фокус на открыватель", st["open"] is False and not st["lock"] and "s-hero__link" in st["f"], str(st))

        to(p, ".contact__panel", -300)
        p.wait_for_timeout(1500)
        p.locator(".cp__field").nth(1).click()
        p.wait_for_timeout(600)
        check("форма: тап по полю «Телефон» панели — фокус в телефоне", p.evaluate("document.activeElement.id") == "f-phone")
        p.locator(".sheet__close").click()
        p.wait_for_timeout(600)

        p.locator(".fmt__link").nth(1).click()
        p.wait_for_timeout(500)
        check("форма: «Обсудить корпоративный бал →» — формат в скрытом поле",
              p.evaluate("document.querySelector('#form [name=format]').value") == "Корпоративный бал")
        p.locator(".sheet__submit").click()
        p.wait_for_timeout(200)
        st = p.evaluate("""() => [...document.querySelectorAll('#form .field__in')].slice(0, 2).map(i => [i.getAttribute('aria-invalid'),
            !document.getElementById(i.getAttribute('aria-describedby')).hidden])""")
        check("форма: пустая отправка — ошибки у имени и телефона", st == [["true", True], ["true", True]], str(st))
        check("форма: фокус на первом поле с ошибкой", p.evaluate("document.activeElement.id") == "f-name")
        p.fill("#f-name", "Анна")
        p.fill("#f-phone", "+7 916 123-45-67")
        check("форма: ошибка снимается при вводе", p.evaluate("document.querySelector('#f-name').getAttribute('aria-invalid')") == "false")
        h0 = p.evaluate("document.querySelector('#f-message').offsetHeight")
        p.fill("#f-message", "Юбилей родителей, около шестидесяти гостей, весной. " * 4)
        p.evaluate("document.querySelector('#f-message').dispatchEvent(new Event('input'))")
        h1 = p.evaluate("document.querySelector('#f-message').offsetHeight")
        check("форма: «Несколько слов» растёт с текстом", h1 > h0, f"{h0} → {h1}")
        p.locator(".sheet__submit").click()
        p.wait_for_timeout(1100)
        st = p.evaluate("() => ({ done: !document.querySelector('[data-view=done]').hidden, f: document.activeElement.className })")
        check("форма: отправка (имитация) — «Заявка отправлена», фокус на заголовке", st["done"] and "sheet__done-h" in st["f"], str(st))
        p.locator(".sheet__close").click()
        p.wait_for_timeout(600)
        p.locator(".cta__link").click()
        p.wait_for_timeout(500)
        check("форма: повторное открытие — снова поля, пустые",
              p.evaluate("!document.querySelector('[data-view=form]').hidden && document.querySelector('#f-name').value === ''"))
        p.keyboard.press("Escape")
        p.wait_for_timeout(600)

        # Меню «Связаться» → шторка закрывается, лист открывается; после закрытия фокус на «Меню»
        p.locator(".site-header__menu").click()
        p.wait_for_timeout(800)
        p.locator(".menu__item[data-form]").click()
        p.wait_for_timeout(900)
        st = p.evaluate("() => ({ open: document.getElementById('form').open, menu: document.getElementById('menu').dataset.state })")
        check("форма: «Связаться» в меню — шторка закрыта, лист открыт", st == {"open": True, "menu": "closed"}, str(st))
        p.keyboard.press("Escape")
        p.wait_for_timeout(600)
        check("форма: после закрытия фокус на «Меню»", "site-header__menu" in p.evaluate("document.activeElement.className"))

        # Клавиатура: Tab — линия 2 px у поля, мышь — без подсветки
        p.locator(".cta__link").click()
        p.wait_for_timeout(500)
        p.locator("#f-name").click()
        p.wait_for_timeout(250)
        sh0 = p.evaluate("getComputedStyle(document.activeElement).boxShadow")
        p.keyboard.press("Tab")
        p.keyboard.press("Shift+Tab")
        p.wait_for_timeout(250)
        sh1 = p.evaluate("getComputedStyle(document.activeElement).boxShadow")
        check("форма: фокус мышью без подсветки, с клавиатуры — линия 2 px", sh0 == "none" and sh1 != "none", f"{sh0} / {sh1}")
        ctx.close()

        ctx = b.new_context(viewport={"width": 390, "height": 844})
        p = ctx.new_page()
        p.goto(url_for(base, "site/index.html") + "?form=error", wait_until="networkidle")
        p.evaluate("document.querySelector('.cta__link').click()")
        p.wait_for_timeout(500)
        p.fill("#f-name", "Анна")
        p.fill("#f-phone", "+7 916 123-45-67")
        p.locator(".sheet__submit").click()
        p.wait_for_timeout(1100)
        check("форма: ?form=error — сообщение о сбое, поля на месте",
              p.evaluate("!document.querySelector('.sheet__fail').hidden && !document.querySelector('[data-view=form]').hidden"))
        ctx.close()

        # --- Шапка над панелью формы ---
        for w in (390, 834, 1440):
            ctx, p = open_page(b, base, w, 900, reduced=True)
            p.evaluate("""() => { const r = document.querySelector('.contact__panel').getBoundingClientRect();
                scrollTo({ top: r.top + scrollY - 10, behavior: 'instant' }); }""")
            p.wait_for_timeout(500)
            st = p.evaluate("""() => ({ menu: document.querySelector('.site-header__menu').dataset.over || '',
                logo: document.querySelector('.site-header__logo').dataset.over || '' })""")
            want = {"menu": "light", "logo": "light" if w < 600 else ""}
            if p.evaluate("document.querySelector('.contact__panel').getBoundingClientRect().top > 32"):
                check(f"шапка над панелью формы ({w}): панель не доезжает до шапки (конец страницы) — шапка без изменений", st == {"menu": "", "logo": ""}, str(st))
                ctx.close()
                continue
            check(f"шапка над панелью формы ({w}): «Меню» Ink" + (", логотип Ink" if w < 600 else ", логотип светлый"), st == want, str(st))
            ctx.close()

        # --- Без JS ---
        ctx = b.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False)
        p = ctx.new_page()
        p.goto(url_for(base, "site/index.html"), wait_until="networkidle")
        st = p.evaluate("""() => ({ sheet: getComputedStyle(document.getElementById('form')).display,
            panel: getComputedStyle(document.querySelector('.contact__panel')).display,
            k: getComputedStyle(document.querySelector('.eves__panel[data-i="2"]')).visibility,
            f2: getComputedStyle(document.querySelector('.eves__frame[data-i="2"]')).display })""")
        check("без JS: лист формы на странице, панели нет, оба описания 10 видны, кадр 2 скрыт",
              st == {"sheet": "block", "panel": "none", "k": "visible", "f2": "none"}, str(st))
        ctx.close()
        b.close()

    print(f"\n{sum(results)} / {len(results)}")


if __name__ == "__main__":
    main()
