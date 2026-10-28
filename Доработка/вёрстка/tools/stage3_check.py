"""Проверка поведения этапа 3: 01 Подготовка, 02 Вечер, 03 Музыка, 04 Танцмейстер.

  python tools/stage3_check.py            # chromium
  python tools/stage3_check.py -b webkit

Печатает «ok / !!» по пунктам. Раскадровки входа вертикальных гигантов (телефон 01 и 04, планшет 01) → сверка/01, сверка/04.
"""
import argparse

from playwright.sync_api import sync_playwright

from _serve import SVERKA, WIDTHS, serve, url_for

results = []


def check(name, ok, info=""):
    results.append(ok)
    print(("ok  " if ok else "!!  ") + name + (f" — {info}" if info else ""))


def open_page(b, base, w, h, reduced=False):
    ctx = b.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce" if reduced else "no-preference")
    p = ctx.new_page()
    p.goto(url_for(base, "site/index.html"), wait_until="networkidle")
    p.evaluate("document.fonts.ready")
    p.wait_for_timeout(300)
    return ctx, p


def to(p, sel, dy=0):
    p.evaluate("([s, dy]) => scrollTo({ top: document.querySelector(s).getBoundingClientRect().top + scrollY + dy, behavior: 'instant' })", [sel, dy])
    p.wait_for_timeout(150)


def storyboard(p, sel, out, prefix, clip_h):
    """Вход на паузе: 0 / 25 / 100 % окна анимаций секции (время берётся по самой долгой)."""
    to(p, sel, -int(p.viewport_size["height"] * 0.5))
    p.wait_for_timeout(60)
    total = p.evaluate("""s => { const a = document.getAnimations().filter(a => document.querySelector(s).contains(a.effect.target));
        a.forEach(x => x.pause()); return Math.max(...a.map(x => x.effect.getComputedTiming().endTime)); }""", sel)
    for pct in (0, 25, 100):
        p.evaluate("([s, t]) => document.getAnimations().filter(a => document.querySelector(s).contains(a.effect.target)).forEach(a => a.currentTime = t)",
                   [sel, total * pct / 100])
        p.wait_for_timeout(60)
        box = p.locator(sel).bounding_box()
        p.screenshot(path=str(out / f"{prefix}_in{pct}.png"),
                     clip={"x": 0, "y": max(0, box["y"]), "width": p.viewport_size["width"], "height": clip_h})
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    a = ap.parse_args()
    sfx = "" if a.browser == "chromium" else "_webkit"
    with serve() as base, sync_playwright() as pw:
        b = getattr(pw, a.browser).launch()

        # --- Горизонтальный скролл страницы ---
        bad = []
        for w in WIDTHS:
            ctx, p = open_page(b, base, w, 900, reduced=True)
            sw = p.evaluate("document.documentElement.scrollWidth")
            if sw > w:
                bad.append(f"{w}: {sw}")
            ctx.close()
        check("нет горизонтального скролла на " + "/".join(map(str, WIDTHS)), not bad, ", ".join(bad))

        # --- 01 и 04 телефон: вертикальные гиганты ---
        ctx, p = open_page(b, base, 390, 844)
        to(p, ".prep__list", -300)
        p.wait_for_timeout(2200)
        info = p.evaluate("""() => { const w = document.querySelector('.prep__step:nth-child(5) .prep__word');
            const r = w.getBoundingClientRect(), ls = w.querySelectorAll('.g-l');
            const first = ls[0].getBoundingClientRect(), last = ls[ls.length - 1].getBoundingClientRect();
            return { h: Math.round(r.height), w: Math.round(r.width), n: ls.length, up: first.top > last.top, mode: getComputedStyle(w).writingMode }; }""")
        check("01 телефон: ВОСПОМИНАНИЯ вертикально, снизу вверх, 506 ± 4 px", info["up"] and abs(info["h"] - 506) <= 4 and info["mode"].startswith("vertical"), str(info))
        check("01 телефон: буквы разбиты (12)", info["n"] == 12)
        lens = p.evaluate("[...document.querySelectorAll('.prep__word')].map(w => Math.round(w.getBoundingClientRect().height))")
        check("01 телефон: длины слов как в Figma (294 / 364 / 355 / 183 / 506 ± 4)",
              all(abs(x - y) <= 4 for x, y in zip(lens, [294, 364, 355, 183, 506])), str(lens))
        out = SVERKA / ("01" + sfx)
        out.mkdir(parents=True, exist_ok=True)
        p.evaluate("history.scrollRestoration = 'manual'; scrollTo(0, 0)")
        p.reload(wait_until="networkidle")
        p.evaluate("document.fonts.ready")
        p.wait_for_timeout(300)
        to(p, ".prep__step:nth-child(2)", -int(844 * 0.9) + 10)
        t = storyboard(p, ".prep__step:nth-child(2)", out, "v3_m_prep", 600)
        check("01 телефон: вход КОНЦЕПЦИИ ≈ 1,3 с", 1100 < t < 1700, f"{t:.0f} мс")
        to(p, ".dm__panel[data-panel=participants]", -200)
        p.wait_for_timeout(2200)
        info = p.evaluate("""() => { const w = document.querySelector('[data-panel=participants] .dm__word'), ph = w.parentElement.querySelector('.dm__photo');
            const l = w.querySelectorAll('.g-l'), f = l[0].getBoundingClientRect(), r = ph.getBoundingClientRect();
            return { bottomGap: Math.round(r.bottom - f.bottom), n: l.length, up: f.top > l[l.length-1].getBoundingClientRect().top }; }""")
        check("04 телефон: УЧАСТНИКИ от низа фото вверх", info["up"] and abs(info["bottomGap"]) <= 3 and info["n"] == 9, str(info))
        out4 = SVERKA / ("04" + sfx)
        out4.mkdir(parents=True, exist_ok=True)
        p.evaluate("history.scrollRestoration = 'manual'; scrollTo(0, 0)")
        p.reload(wait_until="networkidle")
        p.evaluate("document.fonts.ready")
        p.wait_for_timeout(300)
        to(p, ".dm__panel[data-panel=participants] .dm__photo", -int(844 * 0.9) + 10)
        storyboard(p, ".dm__panel[data-panel=participants]", out4, "v3_m_dm", 700)

        # --- 03 телефон: карусель и счётчик ---
        to(p, ".music__rail", -300)
        p.wait_for_timeout(300)
        p.evaluate("document.querySelector('.music__rail').scrollTo({ left: 326, behavior: 'instant' })")
        p.wait_for_timeout(600)
        c2 = p.evaluate("document.querySelector('.music__count-n').textContent")
        p.evaluate("document.querySelector('.music__rail').scrollTo({ left: 9999, behavior: 'instant' })")
        p.wait_for_timeout(600)
        c3 = p.evaluate("document.querySelector('.music__count-n').textContent")
        snap = p.evaluate("""() => { const c = document.querySelectorAll('.music__card')[2].getBoundingClientRect(); return Math.round(c.left + c.width / 2); }""")
        check("03 телефон: счётчик 02 → 03 по ленте", c2 == "02" and c3 == "03", f"{c2}, {c3}")
        check("03 телефон: последняя карточка по центру (195 ± 2)", abs(snap - 195) <= 2, str(snap))
        ctx.close()

        # --- 01 планшет: вход по горизонтали, без переносов ---
        ctx, p = open_page(b, base, 600, 960)
        w = p.evaluate("Math.max(...[...document.querySelectorAll('.prep__word')].map(w => w.scrollWidth - w.clientWidth))")
        check("01 на 600: слова в колонке", w <= 0, str(w))
        ctx.close()
        ctx, p = open_page(b, base, 834, 1194)
        out.mkdir(parents=True, exist_ok=True)
        to(p, ".prep__step:nth-child(5)", -int(1194 * 0.9) + 10)
        storyboard(p, ".prep__step:nth-child(5)", out, "v3_t_prep", 400)
        q = p.evaluate("(() => { const e = document.querySelector('.dm__q1'); return [e.getClientRects().length, Math.round(e.getBoundingClientRect().width)]; })()")
        check("04 планшет: «Выйти танцевать» одной строкой", q[0] == 1 and q[1] <= 770, str(q))
        ctx.close()

        # --- Десктоп ---
        ctx, p = open_page(b, base, 1440, 932)
        to(p, ".prep__list")
        box = p.locator(".prep__step:nth-child(3) .prep__word").bounding_box()
        p.mouse.move(box["x"] + 50, box["y"] + 30)
        p.wait_for_timeout(700)
        st = p.evaluate("""() => ({ s: document.querySelector('.s-prep').dataset.state,
            on: [...document.querySelectorAll('.prep__step')].findIndex(x => x.hasAttribute('data-on')) + 1,
            op: getComputedStyle(document.querySelector('.prep__step:nth-child(3) .prep__more-in')).opacity })""")
        check("01: наведение раскрывает строку 03", st["s"] == "3" and st["on"] == 3 and st["op"] == "1", str(st))
        p.mouse.move(700, 5)
        p.wait_for_timeout(700)
        check("01: уход курсора — покой", p.evaluate("document.querySelector('.s-prep').dataset.state") == "rest")
        p.focus(".prep__step:nth-child(5)")
        p.wait_for_timeout(100)
        check("01: фокус с клавиатуры раскрывает строку", p.evaluate("document.querySelector('.s-prep').dataset.state") == "5")

        # 02 (Ц3): закреплённая сцена, пять этапов по прокрутке; фото — плёнка, слово — барабан (data-pos у этапов)
        to(p, ".eve__track")
        p.wait_for_timeout(1200)
        ev = """() => { const s = document.querySelector('.s-evening'), t = s.querySelector('.eve__track'), st = s.querySelector('.eve__stage');
            const a = s.querySelector('.eve__step[data-pos="active"]');
            return { pin: s.hasAttribute('data-pin'), i: a && a.dataset.i, stage: Math.round(st.getBoundingClientRect().top),
                travel: t.offsetHeight - st.offsetHeight, top: t.getBoundingClientRect().top + scrollY,
                photo: Math.round(a.querySelector('picture').getBoundingClientRect().top - a.querySelector('.eve__photo').getBoundingClientRect().top),
                pos: [...s.querySelectorAll('.eve__step')].map(x => x.dataset.pos).join(' ') }; }"""
        e = p.evaluate(ev)
        check("02: сцена закреплена, этап 1, фото в окне", e["pin"] and e["i"] == "1" and e["stage"] == 0 and e["photo"] == 0, str(e))
        p.evaluate(f"scrollTo({{ top: {e['top'] + e['travel'] / 2}, behavior: 'instant' }})")
        p.wait_for_timeout(1500)
        e2 = p.evaluate(ev)
        check("02: середина дорожки — этап 3, сцена стоит, 1–2 before, 4–5 after",
              e2["i"] == "3" and e2["stage"] == 0 and e2["photo"] == 0 and e2["pos"] == "before before active after after", str(e2))
        p.evaluate(f"scrollTo({{ top: {e['top'] + e['travel']}, behavior: 'instant' }})")
        p.wait_for_timeout(1500)
        check("02: конец дорожки — этап 5", p.evaluate(ev)["i"] == "5")

        # 03: переключатель
        to(p, ".music__track", -300)
        box = p.locator('.music__card[data-i="3"]').bounding_box()
        p.mouse.move(box["x"] + 60, box["y"] + 60)
        p.wait_for_timeout(700)
        s3 = p.evaluate("""() => ({ s: document.querySelector('.s-music').dataset.state,
            shot: getComputedStyle(document.querySelector('.music__shot[data-i="3"]')).opacity })""")
        check("03: наведение на колонку 03 — её фото", s3["s"] == "3" and s3["shot"] == "1", str(s3))
        p.mouse.move(700, 5)
        p.wait_for_timeout(300)
        check("03: уход курсора состояние не сбрасывает", p.evaluate("document.querySelector('.s-music').dataset.state") == "3")

        # 04: панели
        to(p, ".dm__stage", -100)
        box = p.locator(".dm__stage").bounding_box()
        p.mouse.move(box["x"] + 1200, box["y"] + 300)
        p.wait_for_timeout(700)
        d = p.evaluate("""() => ({ s: document.querySelector('.s-dancemaster').dataset.state,
            clip: getComputedStyle(document.querySelector('[data-panel=participants]')).clipPath,
            dim: getComputedStyle(document.querySelector('[data-panel=spectators]'), '::after').opacity })""")
        check("04: наведение на «Участников» раскрывает панель", d["s"] == "participants" and d["dim"] == "0.5", str(d))
        p.mouse.move(300, box["y"] + 300)
        p.wait_for_timeout(700)
        check("04: граница наведения уехала с панелью (x 300 — «Зрители»)", p.evaluate("document.querySelector('.s-dancemaster').dataset.state") == "spectators")
        p.mouse.move(700, 5)
        p.wait_for_timeout(700)
        check("04: уход со сцены — покой", p.evaluate("document.querySelector('.s-dancemaster').dataset.state") == "rest")
        ctx.close()

        # --- reduced-motion: всё в покое ---
        ctx, p = open_page(b, base, 390, 844, reduced=True)
        to(p, "#dancemaster")
        hidden = p.evaluate("[...document.querySelectorAll('#prep [data-reveal], #dancemaster [data-giant]')].filter(e => getComputedStyle(e).opacity !== '1').length")
        check("reduced-motion: входы не прячут текст", hidden == 0, str(hidden))
        ctx.close()
        b.close()
    print(f"\n{sum(results)} / {len(results)}")


if __name__ == "__main__":
    main()
