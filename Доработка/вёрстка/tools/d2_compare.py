"""Д2: сверка «Форматов» и hero с кадрами B (секция Figma 302:1492) на проверочных окнах — картинкой и цифрами.

  python tools/d2_compare.py               # → сверка/d2/pair_<окно>.png (сверху Figma, снизу сайт) + таблица отклонений
  python tools/d2_compare.py -b webkit

Кадры Figma — .figma-shots/d2b_<ширина>_<hero|rest|private|corporate>.png (d2b2_ — исправленные 1024).
Цифры: верх и левый край узлов кадров B против getBoundingClientRect сайта (относительно верха блока). Порог — 4 px.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve, url_for
from pilot_shots import STILL, eager

SHOTS = Path(r"C:\Users\ogare\Desktop\Мои документы\VS CODE\.figma-shots")
WINDOWS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
STATES = [("hero", None), ("rest", None), ("private", 0.15), ("corporate", 0.9)]

# Кадры B: (x, y) верхнего левого угла узла; None — узел скрыт в этом состоянии
FIGMA = {
    (1440, 900): {
        "rest": {"t1": (64, 310), "t2": (784, 310), "n1": (64, 432), "w1": (128, 432), "n2": (784, 432), "w2": (848, 432),
                 "p1": (648, 432), "p2": (1368, 432), "giant": (64, -45)},
        "private": {"giant": (64, 313), "t1": (64, 240), "n1": (64, 104), "w1": (128, 104), "n2": (1112, 104), "d1": (624, 104), "l1": (624, 820)},
        "corporate": {"giant": (64, 313), "t2": (424, 240), "n1": (64, 104), "n2": (424, 104), "w2": (488, 104), "d2": (960, 104), "l2": (960, 820)},
        "hero": {"giant": (64, 496), "c1": (64, 152), "c2": (720, 210), "link": (720, 300)},
    },
    (1920, 950): {
        "rest": {"t1": (64, 327.2), "t2": (1024, 327.2), "n1": (64, 456), "w1": (151.4, 456), "n2": (1024, 456), "w2": (1111.4, 456),
                 "p1": (888, 456), "p2": (1848, 456), "giant": (64, -47.5)},
        "private": {"giant": (64, 330.4), "t1": (64, 253.3), "n1": (64, 104), "w1": (151.4, 104), "n2": (1483.7, 104), "d1": (995.7, 104), "l1": (995.7, 865.6)},
        "corporate": {"giant": (64, 330.4), "t2": (532.3, 253.3), "n1": (64, 104), "n2": (532.3, 104), "w2": (619.7, 104), "d2": (1440, 104), "l2": (1440, 865.6)},
        "hero": {"giant": (64, 523.6), "c1": (64, 160.4), "c2": (960, 221.7), "link": (960, 316.7)},
    },
    (1366, 650): {
        "rest": {"t1": (64, 223.9), "t2": (747, 223.9), "n1": (64, 312), "w1": (124.4, 312), "n2": (747, 312), "w2": (807.4, 312),
                 "p1": (611, 312), "p2": (1294, 312), "giant": (64, -32.5)},
        "private": {"giant": (64, 259.7), "t1": (64, 207), "n1": (64, 104), "w1": (124.4, 104), "n2": (1054.7, 104), "d1": (586.8, 104), "l1": (586.8, 592.2)},
        "corporate": {"giant": (64, 259.7), "t2": (407.3, 207), "n1": (64, 104), "n2": (407.3, 104), "w2": (467.7, 104), "d2": (901, 104), "l2": (901, 592.2)},
    },
    (1280, 600): {
        "rest": {"t1": (64, 206.7), "t2": (704, 206.7), "n1": (64, 288), "w1": (120.2, 288), "n2": (704, 288), "w2": (760.2, 288),
                 "p1": (568, 288), "p2": (1208, 288), "giant": (64, -30)},
        "private": {"giant": (64, 260.7), "t1": (64, 212), "n1": (64, 104), "w1": (120.2, 104), "n2": (988.1, 104), "d1": (543.7, 104), "l1": (543.7, 546.7)},
        "corporate": {"giant": (64, 260.7), "t2": (387.9, 212), "n1": (64, 104), "n2": (387.9, 104), "w2": (444.1, 104), "d2": (815, 104), "l2": (815, 546.7)},
    },
    (1024, 650): {
        "rest": {"t1": (64, 211.7), "t2": (576, 211.7), "n1": (64, 295), "w1": (107.7, 295), "n2": (576, 277), "w2": (619.7, 277),
                 "p1": (440, 295), "p2": (952, 295), "giant": (64, -30.7)},
        "private": {"giant": (64, 357.9), "t1": (64, 308), "n1": (64, 104), "w1": (107.7, 104), "n2": (789.9, 104), "d1": (381.9, 104), "l1": (381.9, 595.4)},
        "corporate": {"giant": (64, 357.9), "t2": (330.1, 308), "n1": (64, 104), "n2": (330.1, 104), "w2": (373.9, 104), "d2": (559, 104), "l2": (559, 595.4)},
        "hero": {"giant": (64, 374.1), "c1": (64, 103.8), "c2": (512, 143.4), "link": (512, 204.9)},
    },
}

# Узлы сайта: текстовые — по строке (Range), чтобы сравнивать с рамкой текста Figma
SITE_JS = """() => {
  const f = document.querySelector('#formats'), top = f.getBoundingClientRect().top;
  const q = (s) => document.querySelector(s);
  const box = (el) => { const r = el.getBoundingClientRect(); return [r.left, r.top - top]; };
  const P = '[data-half=private] ', C = '[data-half=corporate] ';
  const link = (el) => { const r = el.getBoundingClientRect(); return [r.left, r.top + 8 - top]; };
  const out = {
    giant: box(q('.hf__giant-in')), t1: box(q(P + '.fmt__title')), t2: box(q(C + '.fmt__title')),
    n1: box(q(P + '.fmt__num')), w1: box(q(P + '.fmt__whom')), n2: box(q(C + '.fmt__num')), w2: box(q(C + '.fmt__whom')),
    p1: box(q(P + '.fmt__plus')), p2: box(q(C + '.fmt__plus')), d1: box(q(P + '.fmt__desc')), d2: box(q(C + '.fmt__desc')),
    l1: link(q(P + '.fmt__link')), l2: link(q(C + '.fmt__link')),
    c1: box(q('.s-hero__line')), c2: [box(q('.s-hero__line--2 em'))[0], box(q('.s-hero__line--2'))[1]], link: box(q('.s-hero__link')),
  };
  return out;
}"""


def shoot(browser, base, w, h, out, engine):
    ctx = browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(url_for(base, "site/index.html"), wait_until="networkidle")
    eager(page)
    page.add_style_tag(content=STILL)
    page.wait_for_timeout(300)
    files, meas = {}, {}
    for name, fx in STATES:
        if name == "hero":
            page.evaluate("scrollTo({top: 0, behavior: 'instant'})")
            page.mouse.move(w / 2, 2)
        else:
            if name == "rest":
                top = page.evaluate("document.querySelector('#formats').getBoundingClientRect().top + scrollY")
                page.evaluate("y => scrollTo({top: y, behavior: 'instant'})", top)
            page.mouse.move(w * fx if fx else w / 2, h * 0.7 if fx else 2)
            if not fx:
                page.evaluate("document.querySelector('#formats').dispatchEvent(new PointerEvent('pointerleave', {pointerType: 'mouse'}))")
        page.wait_for_timeout(250)
        f = out / f"site_{engine}_{w}x{h}_{name}.png"
        page.screenshot(path=str(f))
        files[name] = f
        m = page.evaluate(SITE_JS)
        if name == "hero":
            # hero: координаты от верха страницы (Форматы ниже на высоту hero)
            m = {k: [v[0], v[1] + h] for k, v in m.items()}
        meas[name] = m
    ctx.close()
    return files, meas


def figma_file(w, name):
    for pre in ("d2b2", "d2b"):
        f = SHOTS / f"{pre}_{w}_{name}.png"
        if f.exists():
            return f
    return None


def pair_sheet(w, h, files, path, col_w=700):
    font = ImageFont.truetype("arial.ttf", 20)
    pad, head = 12, 28
    rows = [("Figma B", [figma_file(w, n) for n, _ in STATES]), ("Сайт", [files[n] for n, _ in STATES])]
    th = round(h * col_w / w)
    out = Image.new("RGB", (pad + len(STATES) * (col_w + pad), pad + len(rows) * (head + th + pad)), (40, 40, 40))
    d = ImageDraw.Draw(out)
    y = pad
    for label, fs in rows:
        d.text((pad, y), f"{w}×{h} · {label}", fill=(220, 215, 205), font=font)
        y += head
        for i, f in enumerate(fs):
            if f:
                out.paste(Image.open(f).convert("RGB").resize((col_w, th)), (pad + i * (col_w + pad), y))
        y += th + pad
    out.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    args = ap.parse_args()
    out = SVERKA / "d2"
    out.mkdir(parents=True, exist_ok=True)
    worst = 0
    with serve() as base, sync_playwright() as p:
        browser = getattr(p, args.browser).launch()
        for w, h in WINDOWS:
            files, meas = shoot(browser, base, w, h, out, args.browser)
            pair_sheet(w, h, files, out / f"pair_{args.browser}_{w}x{h}.png")
            for state, nodes in FIGMA[(w, h)].items():
                bad = []
                for k, (fx, fy) in nodes.items():
                    sx, sy = meas[state][k]
                    dx, dy = sx - fx, sy - fy
                    worst = max(worst, abs(dx), abs(dy))
                    if abs(dx) > 4 or abs(dy) > 4:
                        bad.append(f"{k} Δx {dx:+.1f} Δy {dy:+.1f}")
                print(f"{'ok ' if not bad else '!! '} {w}×{h} {state:9}" + ("" if not bad else " — " + "; ".join(bad)))
        browser.close()
    print(f"наибольшее отклонение {worst:.1f} px")


if __name__ == "__main__":
    main()
