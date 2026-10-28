"""Проверка поведения этапа 4: 05 Шоу, 06 Ассистент, 07 Уроки (после Ц3 — только горизонтальный скролл), 08 Этикет (после Ц2 — только горизонтальный скролл).

  python tools/stage4_check.py            # chromium
  python tools/stage4_check.py -b webkit

Печатает «ok / !!» по пунктам. Раскадровки входа 05 и 06 на телефоне → сверка/05, сверка/06.
"""
import argparse

from playwright.sync_api import sync_playwright

from _serve import SVERKA, WIDTHS, serve, url_for

results = []


def check(name, ok, info=""):
    results.append(ok)
    print(("ok  " if ok else "!!  ") + name + (f" — {info}" if info else ""))


def open_page(b, base, w, h, reduced=False, touch=False):
    ctx = b.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce" if reduced else "no-preference", has_touch=touch)
    p = ctx.new_page()
    p.add_init_script("history.scrollRestoration = 'manual'")
    p.goto(url_for(base, "site/index.html"), wait_until="networkidle")
    p.evaluate("document.fonts.ready")
    p.wait_for_timeout(300)
    return ctx, p


def to(p, sel, dy=0):
    p.evaluate("([s, dy]) => scrollTo({ top: document.querySelector(s).getBoundingClientRect().top + scrollY + dy, behavior: 'instant' })", [sel, dy])
    p.wait_for_timeout(200)


def touch_swipe(p, sel, dx):
    p.evaluate("""([s, dx]) => { const el = document.querySelector(s), r = el.getBoundingClientRect();
        const x = r.left + r.width / 2, y = r.top + Math.min(r.height / 2, 200);
        const o = { pointerType: 'touch', isPrimary: true, pointerId: 7, bubbles: true };
        el.dispatchEvent(new PointerEvent('pointerdown', { ...o, clientX: x, clientY: y }));
        el.dispatchEvent(new PointerEvent('pointerup', { ...o, clientX: x + dx, clientY: y + 4 })); }""", [sel, dx])
    p.wait_for_timeout(100)


def step(p):
    return p.evaluate("document.querySelector('.s-show').dataset.step")


def storyboard(p, sel, out, prefix, clip_h):
    to(p, sel, -int(p.viewport_size["height"] * 0.5))
    p.wait_for_timeout(60)
    total = p.evaluate("""s => { const a = document.getAnimations().filter(a => a.effect && document.querySelector(s).contains(a.effect.target));
        a.forEach(x => x.pause()); return a.length ? Math.max(...a.map(x => x.effect.getComputedTiming().endTime)) : 0; }""", sel)
    for pct in (0, 25, 100):
        p.evaluate("([s, t]) => document.getAnimations().filter(a => a.effect && document.querySelector(s).contains(a.effect.target)).forEach(a => a.currentTime = t)",
                   [sel, total * pct / 100])
        p.wait_for_timeout(60)
        box = p.locator(sel).first.bounding_box()
        p.screenshot(path=str(out / f"{prefix}_in{pct}.png"),
                     clip={"x": 0, "y": max(0, box["y"]), "width": p.viewport_size["width"], "height": clip_h})
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    a = ap.parse_args()
    with serve() as base, sync_playwright() as pw:
        b = getattr(pw, a.browser).launch()

        # --- Горизонтальный скролл страницы ---
        bad = []
        for w in WIDTHS:
            ctx, p = open_page(b, base, w, 900)
            for sel in (".s-show", ".s-assistant", ".s-lessons", ".s-etiquette"):
                to(p, sel)
            sw = p.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            if sw > 0:
                bad.append(f"{w}: {sw}px")
            ctx.close()
        check("нет горизонтального скролла на 360…1920", not bad, ", ".join(bad))

        # --- 05 телефон: вертикальное слово от низа фото, свайп, тап, счётчик, вход ---
        ctx, p = open_page(b, base, 390, 844, touch=True)
        geo = p.evaluate("""() => { const sc = document.querySelector('.show__scene').getBoundingClientRect();
            const w = document.querySelector('.show__word[data-i="1"] .show__line').getBoundingClientRect();
            return { scB: sc.bottom, wB: w.bottom, wH: w.height, wL: w.left }; }""")
        check("05 телефон: ПРОФЕССИОНАЛЫ снизу вверх от низа фото", abs(geo["wB"] - geo["scB"]) < 2 and abs(geo["wL"] - 16) < 1.5,
              f"низ слова {geo['wB']:.0f} / фото {geo['scB']:.0f}, длина {geo['wH']:.0f} (Figma 551), x {geo['wL']:.1f}")
        out = SVERKA / "05"
        out.mkdir(parents=True, exist_ok=True)
        total = storyboard(p, ".show__stage", out, "v4_m_show_story", 844)
        check("05 телефон: вход ПРОФЕССИОНАЛЫ ≈ 1,55 с", 1450 <= total <= 1700, f"{total:.0f} мс")
        p.evaluate("document.getAnimations().forEach(a => a.finish())")
        anim2 = p.evaluate("[...document.querySelectorAll('.show__word[data-i=\"2\"] [data-giant]')].every(g => !g.querySelector('.g-l'))")
        check("05: слова неактивных форматов без входа (не разбиты на буквы)", anim2)
        touch_swipe(p, ".show__stage", -120)
        s1 = step(p)
        touch_swipe(p, ".show__stage", -120)
        s2 = step(p)
        touch_swipe(p, ".show__stage", 120)
        s3 = step(p)
        touch_swipe(p, ".show__stage", 20)
        s4 = step(p)
        check("05 телефон: свайп влево — вперёд, вправо — назад, короткий жест не считается", [s1, s2, s3, s4] == ["2", "3", "2", "2"], str([s1, s2, s3, s4]))
        p.evaluate("document.querySelectorAll('.show__tab')[2].click()")
        p.wait_for_timeout(100)
        mid = p.evaluate("""() => { const f = document.querySelector('.show__frame[data-i="3"]'); return getComputedStyle(f).clipPath; }""")
        p.wait_for_timeout(1400)
        st = p.evaluate("""() => ({ step: document.querySelector('.s-show').dataset.step,
            n: document.querySelector('.show__count-n').textContent,
            on: [...document.querySelectorAll('.show__desc')].map(d => d.hasAttribute('data-on') ? 1 : 0).join(''),
            sel: [...document.querySelectorAll('.show__tab')].map(t => t.getAttribute('aria-selected') === 'true' ? 1 : 0).join(''),
            mark: getComputedStyle(document.querySelector('.show__mark')).transform,
            clip: getComputedStyle(document.querySelector('.show__frame[data-i="3"]')).clipPath,
            pos: [...document.querySelectorAll('.show__frame')].map(f => f.dataset.pos).join(',') })""")
        check("05 телефон: тап по пункту 03 — формат, описание, счётчик, линия пункта",
              st["step"] == "3" and st["n"] == "03" and st["on"] == "001" and st["sel"] == "001" and "88" in st["mark"],
              str(st))
        check("05: занавес — clip-path от оси (в середине смены кадр раскрыт частично)", "inset" in mid and st["clip"] in ("inset(0px)", "none"), f"{mid} → {st['clip']}")
        check("05: предыдущие кадры — before, текущий active", st["pos"] == "before,before,active", st["pos"])
        p.focus(".show__tab[aria-selected='true']")
        p.keyboard.press("ArrowRight")
        p.wait_for_timeout(100)
        k = p.evaluate("[document.querySelector('.s-show').dataset.step, document.activeElement.dataset.i]")
        check("05: стрелка → на пунктах — следующий формат по кругу и фокус", k == ["1", "1"], str(k))
        ctx.close()

        # --- 05 планшет: шаг барабана больше окна, слово под фото ---
        ctx, p = open_page(b, base, 834, 1194)
        g = p.evaluate("""() => { const win = document.querySelector('.show__win').getBoundingClientRect();
            const w2 = document.querySelector('.show__word[data-i="2"]').getBoundingClientRect();
            const sc = document.querySelector('.show__scene').getBoundingClientRect();
            return { winH: win.height, off: w2.top - win.top, below: win.bottom - sc.bottom }; }""")
        check("05 планшет: барабан 110, сосед на шаге > окна, окно на 76 ниже фото", abs(g["winH"] - 110) < 1 and g["off"] > 120 and abs(g["below"] - 76) < 1.5, str(g))
        ctx.close()

        # --- 05 десктоп: закрепление, шаг по прокрутке, пункт прокручивает к шагу ---
        ctx, p = open_page(b, base, 1440, 900)
        to(p, ".show__track", -200)
        p.wait_for_timeout(1600)
        info = p.evaluate("""() => { const t = document.querySelector('.show__track'), s = document.querySelector('.show__stage');
            return { th: t.offsetHeight, sh: s.offsetHeight, top: parseFloat(getComputedStyle(s).top), abs: t.getBoundingClientRect().top + scrollY }; }""")
        travel = info["th"] - info["sh"]
        seen, tops = [], []
        for frac in (0.05, 0.3, 0.55, 0.8, 0.98):
            p.evaluate("y => scrollTo({ top: y, behavior: 'instant' })", info["abs"] - info["top"] + frac * travel)
            p.wait_for_timeout(250)
            seen.append(step(p))
            tops.append(round(p.evaluate("document.querySelector('.show__stage').getBoundingClientRect().top")))
        check("05 десктоп: сцена закреплена (окно − шапка), шаги 1→3 по прокрутке",
              seen == ["1", "2", "2", "3", "3"] and len(set(tops)) == 1 and info["sh"] == 828, f"{seen}, top {tops[0]}, сцена {info['sh']}")
        p.evaluate("y => scrollTo({ top: y, behavior: 'instant' })", info["abs"] - info["top"] + 0.02 * travel)
        p.wait_for_timeout(200)
        p.evaluate("document.querySelectorAll('.show__tab')[1].click()")
        p.wait_for_timeout(1500)
        check("05 десктоп: пункт 02 прокручивает к своему шагу", step(p) == "2", step(p))
        ctx.close()

        ctx, p = open_page(b, base, 1440, 900, reduced=True)
        r = p.evaluate("() => [document.querySelector('.show__track').offsetHeight, document.querySelector('.show__stage').offsetHeight]")
        p.evaluate("document.querySelectorAll('.show__tab')[2].click()")
        p.wait_for_timeout(300)
        check("05 десктоп reduced-motion: без закрепления, пункт переключает сразу", r[0] == r[1] and step(p) == "3", f"{r}, шаг {step(p)}")
        ctx.close()

        # --- 06: телефон — вертикальные вопросы в высоте фото; десктоп — наведение, фокус, покоя нет ---
        ctx, p = open_page(b, base, 360, 800)
        q = p.evaluate("""() => [...document.querySelectorAll('.asst__item')].map(it => {
            const ph = it.querySelector('.asst__photo').getBoundingClientRect(), q = it.querySelector('.asst__q').getBoundingClientRect();
            return [Math.round(q.height), Math.round(ph.height), Math.round(q.bottom - ph.bottom), Math.round(q.width)]; })""")
        check("06 на 360: вопросы вертикально, от низа фото, в высоте фото", all(h <= ph and abs(d) <= 1 for h, ph, d, _ in q), str(q))
        ctx.close()

        ctx, p = open_page(b, base, 390, 844)
        out = SVERKA / "06"
        out.mkdir(parents=True, exist_ok=True)
        total = storyboard(p, ".asst__item", out, "v4_m_asst_story", 844)
        check("06 телефон: вход СТЕСНЯЕТЕСЬ ≈ 1,45 с", 1350 <= total <= 1700, f"{total:.0f} мс")
        ctx.close()

        ctx, p = open_page(b, base, 1440, 900)
        to(p, ".asst__list", -200)
        p.wait_for_timeout(1500)
        box = p.locator(".asst__item").nth(2).bounding_box()
        p.mouse.move(box["x"] + 60, box["y"] + 60)
        p.wait_for_timeout(500)
        s1 = p.evaluate("""() => [document.querySelector('.s-assistant').dataset.state,
            ...[...document.querySelectorAll('.asst__photo')].map(e => getComputedStyle(e).opacity)]""")
        p.mouse.move(5, 5)
        p.wait_for_timeout(400)
        s2 = p.evaluate("document.querySelector('.s-assistant').dataset.state")
        p.keyboard.press("Tab")
        p.evaluate("document.querySelectorAll('.asst__item')[1].focus()")
        p.wait_for_timeout(400)
        s3 = p.evaluate("[document.querySelector('.s-assistant').dataset.state, getComputedStyle(document.querySelectorAll('.asst__a')[1]).opacity]")
        check("06 десктоп: наведение на 03 — фото и ответ 03; уход курсора не сбрасывает; фокус на 02",
              s1 == ["3", "0", "0", "1"] and s2 == "3" and s3 == ["2", "1"], f"{s1} / {s2} / {s3}")
        ctx.close()

        # 07 (Ц3): the phone zigzag check is removed (the gist and the 16 / 87 / 158 stairs are gone).
        # 07 stays in the horizontal-scroll loop above, as 08 does after Ц2.

        # Шапка над панелью 08 — снято в Ц2 (у 08 нет светлой панели); шапка над светлым — stage5_check (панель Контактов)

        # --- reduced-motion: всё в покое ---
        ctx, p = open_page(b, base, 390, 844, reduced=True)
        to(p, ".s-show")
        n = p.evaluate("document.getAnimations().length")
        check("reduced-motion: входов нет", n == 0, str(n))
        ctx.close()

        b.close()
    print(f"\n{sum(results)} / {len(results)}")


if __name__ == "__main__":
    main()
