"""Block 07 «Уроки» (#lessons, stage Ц3): comparison with the Figma frames — numbers, image pairs, fit to the window.

  python tools/c3_compare.py              # chromium: part A (deviation table, screenshots), B (pairs), C (windows, widths)
  python tools/c3_compare.py -b webkit
  python tools/c3_compare.py --all        # part A: every point, not only deviations over 4 px

Part A: Figma points against the site, threshold 4 px. Coordinates are section-relative: x from the window's left edge,
y from the top of #lessons. Block boxes are compared (left, top, width, height), except the tablet giant: its x is the
right edge of a Range over its text. The phrase is the .less__phrase box on desktop and tablet, the .less__p1 and
.less__p2 boxes on the phone. Width is compared only where Figma gives it. #lessons is saved for each frame width:
сверка/c3/site_<engine>_<width>.png.
Part B: "Figma | site" pair only for frames with a deviation > 4 px → сверка/c3/pair_<engine>_<width>.png.
The Figma snapshot is read from FIGMA_DIR (the plugin's folder); without it the pair is skipped with a message.
Part C: desktop windows 1440x900 … 1024x650 (section height = window height, all texts inside the section, gaps to the
phrase and the giant, labels on one line) and widths 360 … 1920 without horizontal scroll (block at the top of the
window, then -200 px after 250 ms).

Known and accepted, not fixed: text 2 wraps into 8 lines in the browser where Figma has 7, because of the non-breaking
space in «С&nbsp;юмором». The numbers of that deviation are in the table; they are not corrected here.
"""
import argparse
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve, url_for
from pilot_shots import STILL, eager

TOOLS = Path(__file__).resolve().parent
OUT = SVERKA / "c3"
FIGMA_DIR = Path("C:/Users/ogare/Desktop/Мои документы/VS CODE/.figma-shots")
THRESH = 4
HIDE = ".site-header,.skip{visibility:hidden!important}"          # header and skip link are not in the Figma frames
WINDOWS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
WIDTHS = [360, 390, 600, 834, 1023, 1024, 1280, 1440, 1920]
HEAD = f"{'точка':<9} {'Figma':<26} {'сайт':<34} {'dx':>7} {'dy':>7} {'dw':>7} {'dh':>7}  флаг"
SW = "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"

# frame: (width, window height, Figma frame, Figma snapshot file for the pair)
FRAMES = {
    "1440": (1440, 900, "394:2605", "c3s-d.png"),
    "834": (834, 1112, "T834 / 07 Уроки · Ц3 · покой", "c3s-t.png"),
    "390": (390, 844, "M390 / 07 Уроки · Ц3 · покой", "c3s-m.png"),
}


def P(key, sel, x=None, y=None, w=None, h=None, mode="box"):
    """Figma point. Mode box: the element box. Mode right: the right edge of a DOM Range over the text (tablet giant).
    None means the value is not given in Figma and is not compared."""
    return {"key": key, "sel": sel, "mode": mode, "fig": {"x": x, "y": y, "w": w, "h": h}}


# Figma points (top-left corner of each node, px): x from the window's left edge, y from the top of #lessons
ROWS = {
    "1440": [
        P("section", "#lessons", h=900),
        P("label", ".less__label", 64, 104),
        P("phrase", ".less__phrase", 64, 152, h=120),
        P("giant", ".less__giant", 400, 290, h=170),
        P("stage1", ".less__step:nth-child(1) .less__stage", 64, 640),
        P("stage2", ".less__step:nth-child(2) .less__stage", 400, 680),
        P("stage3", ".less__step:nth-child(3) .less__stage", 720, 720),
        P("text1", ".less__step:nth-child(1) .less__text", 64, 668, 288, 54),
        P("text2", ".less__step:nth-child(2) .less__text", 400, 708, 288, 90),
        P("text3", ".less__step:nth-child(3) .less__text", 720, 748, 288, 36),
    ],
    "834": [
        P("section", "#lessons", h=705),
        P("label", ".less__label", 32, 96),
        P("phrase", ".less__phrase", 32, 140),
        P("em", ".less__p2 em", 498),
        P("giant", ".less__giant", 802, 235, h=78, mode="right"),
        P("stage1", ".less__step:nth-child(1) .less__stage", 32, 433),
        P("stage2", ".less__step:nth-child(2) .less__stage", 300, 473),
        P("stage3", ".less__step:nth-child(3) .less__stage", 568, 513),
        P("text1", ".less__step:nth-child(1) .less__text", 32, 461, 234, 54),
        P("text2", ".less__step:nth-child(2) .less__text", 300, 501, 234, 108),
        P("text3", ".less__step:nth-child(3) .less__text", 568, 541, 234, 54),
    ],
    "390": [
        P("section", "#lessons", h=882),
        P("label", ".less__label", 16, 104),
        P("p1", ".less__p1", 16, 140),
        P("p2", ".less__p2", 66, 182),
        P("giant", ".less__giant", 117, 240, h=38),
        P("stage1", ".less__step:nth-child(1) .less__stage", 16, 374),
        P("stage2", ".less__step:nth-child(2) .less__stage", 87, 514),
        P("stage3", ".less__step:nth-child(3) .less__stage", 158, 702),
        P("text1", ".less__step:nth-child(1) .less__text", 16, 402, 216, 64),
        P("text2", ".less__step:nth-child(2) .less__text", 87, 542, 216, 112),
        P("text3", ".less__step:nth-child(3) .less__text", 158, 730, 216, 48),
    ],
}

# Part A measurement, one call per frame. Coordinates in px: x from the window's left edge (the page has no horizontal
# scroll, so scrollX is 0), y from the top of the reference element (#lessons).
MEASURE = """([rows, refSel]) => {
  const refTop = document.querySelector(refSel).getBoundingClientRect().top + scrollY;
  const out = {};
  for (const r of rows) {
    const el = document.querySelector(r.sel);
    if (!el) { out[r.key] = null; continue; }
    const b = el.getBoundingClientRect();
    let x = b.left + scrollX;
    if (r.mode === 'right') {
      const g = document.createRange();
      g.selectNodeContents(el);
      x = g.getBoundingClientRect().right + scrollX;
    }
    out[r.key] = { x: x, y: b.top + scrollY - refTop, w: b.width, h: b.height };
  }
  return out;
}"""

# Part C measurement, one call per window (#lessons at the top of the window)
MEASURE_C = """() => {
  const q = (s) => document.querySelector(s);
  const R = (el) => { const r = el.getBoundingClientRect(); return { l: r.left, r: r.right, t: r.top, b: r.bottom, h: r.height }; };
  return {
    iw: innerHeight, cw: document.documentElement.clientWidth,
    k: getComputedStyle(q('#lessons')).getPropertyValue('--k7').trim(),
    sec: R(q('#lessons')), label: R(q('.less__label')), phrase: R(q('.less__phrase')), giant: R(q('.less__giant')),
    stage: [1, 2, 3].map((i) => R(q(`.less__step:nth-child(${i}) .less__stage`))),
    text: [1, 2, 3].map((i) => R(q(`.less__step:nth-child(${i}) .less__text`))),
    all: [...document.querySelectorAll('.less__label, .less__phrase, .less__giant, .less__stage, .less__text')]
      .map((e) => ({ n: e.className.split(' ')[0], ...R(e) })),
  };
}"""


def open_page(browser, base, w, h):
    """Site page for comparison: no animations (STILL), lazy images loaded, fonts ready, +300 ms."""
    ctx = browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(url_for(base, "site/index.html"), wait_until="networkidle")
    page.add_style_tag(content=STILL)
    eager(page)
    page.wait_for_timeout(300)
    return ctx, page


def scroll_to(page, sel, dy=0, wait=300):
    """Top of the element to the top of the window (dy is an offset), instant scroll."""
    top = page.evaluate("s => document.querySelector(s).getBoundingClientRect().top + scrollY", sel)
    page.evaluate("y => scrollTo({top: y, behavior: 'instant'})", top + dy)
    page.wait_for_timeout(wait)


def take_shot(page, key, path):
    """#lessons screenshot for a frame width. Desktop: the window from the top of the block (the block is one screen).
    Tablet and phone: the whole #lessons element. The header is hidden by visibility, the layout is unchanged."""
    page.add_style_tag(content=HIDE)
    if key == "1440":
        scroll_to(page, "#lessons")
        page.screenshot(path=str(path))
    else:
        page.locator("#lessons").screenshot(path=str(path))


def compare(r, m):
    """Table row for one point: (row text, has a deviation > 4 px, largest |Δ|, its name)."""
    fig, name = r["fig"], r["key"]
    if m is None:
        return f"{name:<9} нет элемента: {r['sel']}", True, 0.0, name
    given = [f for f in ("x", "y", "w", "h") if fig[f] is not None]
    cells, bad, worst = {}, False, (0.0, name)
    for f in given:
        d = m[f] - fig[f]
        cells[f] = f"{d:+.1f}"
        if abs(d) > worst[0]:
            worst = (abs(d), f"{name}.{f}")
        bad = bad or abs(d) > THRESH
    fig_s = " ".join(f"{f}{fig[f]:g}" for f in given)
    site_s = " ".join(f"{f}{m[f]:.1f}" for f in given)
    dcol = " ".join(f"{cells.get(f, ''):>7}" for f in ("x", "y", "w", "h"))
    return f"{name:<9} {fig_s:<26} {site_s:<34} {dcol}  {'>4' if bad else ''}", bad, worst[0], worst[1]


def part_a(browser, base, engine, show_all=False):
    """Part A: table per frame, #lessons screenshot per width, summary per width. Returns frames with a deviation > 4 px."""
    worst, flagged, summary = 0.0, [], []
    for key, (w, h, name, _) in FRAMES.items():
        ctx, page = open_page(browser, base, w, h)
        meas = page.evaluate(MEASURE, [ROWS[key], "#lessons"])
        bad_n, fw, fp, lines = 0, 0.0, "", []
        for r in ROWS[key]:
            line, bad, rw, rp = compare(r, meas[r["key"]])
            lines.append((line, bad))
            bad_n += bad
            if rw > fw:
                fw, fp = rw, rp
        shown = [line for line, bad in lines if show_all or bad]
        if shown:
            print(f"\n{engine} · {w}x{h} · кадр Figma {name}")
            print(HEAD)
            for line in shown:
                print(line)
            print(f"  кадр: наибольшее отклонение {fw:.1f} px ({fp}), точек > 4 px: {bad_n}")
        else:
            print(f"{engine} · {w}x{h} · кадр Figma {name}: ok (≤{THRESH} px)")
        worst = max(worst, fw)
        summary.append((w, h, fw, fp, bad_n))
        if bad_n:
            flagged.append(key)
        take_shot(page, key, OUT / f"site_{engine}_{key}.png")
        ctx.close()
    print(f"\nсводка · {engine}")
    print(f"{'ширина':<8} {'окно':<10} {'наибольшее |Δ|':>14}  {'точка':<18} точек > 4 px")
    for w, h, fw, fp, n in summary:
        print(f"{w:<8} {f'{w}x{h}':<10} {fw:>11.1f} px  {fp:<18} {n}")
    print("* ширина текста — по коробке элемента, входит в порог")
    print(f"\nнаибольшее отклонение {worst:.1f} px, кадров > 4 px: {len(flagged)}")
    return flagged


def part_b(engine, flagged):
    """Part B: "Figma | site" pairs, only for frames with a deviation > 4 px."""
    print("\nчасть B — пары «Figma | сайт»:")
    if not flagged:
        print("  кадров с отклонением > 4 px нет — пары не собираются")
    for key in flagged:
        fig = FIGMA_DIR / FRAMES[key][3]
        if not fig.exists():
            print(f"  нет снимка Figma: {fig}")
            continue
        out = OUT / f"pair_{engine}_{key}.png"
        subprocess.run([sys.executable, str(TOOLS / "pair.py"), str(fig), str(OUT / f"site_{engine}_{key}.png"), "-o", str(out)],
                       check=True, stdout=subprocess.DEVNULL)
        print(f"  {key}: {out}")


def fit_checks(m, w, h):
    """Part C checks for one window: (header, [(ok, text), ...])."""
    iw, cw, sec = m["iw"], m["cw"], m["sec"]
    ph, gi, lab, st = m["phrase"], m["giant"], m["label"], m["stage"]
    outside = [e["n"] for e in m["all"]
               if e["t"] < sec["t"] - 0.5 or e["b"] > sec["b"] + 0.5 or e["l"] < -0.5 or e["r"] > cw + 0.5]
    gap1 = st[0]["t"] - ph["b"]                                 # fragment 1 below the phrase
    gap2, gap3 = st[1]["t"] - gi["b"], st[2]["t"] - gi["b"]     # fragments 2 and 3 below the giant
    heights = [lab["h"]] + [s["h"] for s in st]
    head = f"окно {w}x{h}: innerHeight {iw}, clientWidth {cw}, --k7 {m['k']}"
    res = [
        (abs(sec["h"] - iw) <= 1, f"1 #lessons высота {sec['h']:.1f} при окне {iw} (±1)"),
        (not outside, f"2 тексты внутри секции ({len(m['all'])} шт.), выход за край: {', '.join(outside) or 'нет'}"),
        (gap1 >= 23, f"3 фрагмент 1 под фразой: низ фразы {ph['b']:.1f}, верх метки {st[0]['t']:.1f}, зазор {gap1:.1f} (>=23)"),
        (gap2 >= 23 and gap3 >= 23,
         f"4 фрагменты 2 и 3 под гигантом: низ гиганта {gi['b']:.1f}, зазоры {gap2:.1f} / {gap3:.1f} (>=23)"),
        (all(v <= 16 for v in heights), f"5 метки в одну строку: высоты {' / '.join(f'{v:.1f}' for v in heights)} (<=16)"),
    ]
    return head, res


def part_c(browser, base):
    """Part C: desktop windows (section at the top of the window) and widths without horizontal scroll."""
    checks = fails = 0
    print("\nчасть C — подгонка под окно (секция у верха окна):")
    for w, h in WINDOWS:
        ctx, page = open_page(browser, base, w, h)
        scroll_to(page, "#lessons")
        m = page.evaluate(MEASURE_C)
        ctx.close()
        head, res = fit_checks(m, w, h)
        print(head)
        for ok, text in res:
            checks += 1
            fails += not ok
            print(f"  {'ok  ' if ok else 'FAIL'} {text}")
    print("\nгоризонтальный скролл, высота 900: scrollWidth - clientWidth у #lessons, затем от блока -200 через 250 мс:")
    for w in WIDTHS:
        ctx, page = open_page(browser, base, w, 900)
        scroll_to(page, "#lessons")
        a = page.evaluate(SW)
        scroll_to(page, "#lessons", dy=-200, wait=250)
        b = page.evaluate(SW)
        ctx.close()
        ok = a == 0 and b == 0
        checks += 1
        fails += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {w}: {a} / {b}")
    print(f"часть C: FAIL {fails} из {checks}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    ap.add_argument("--all", action="store_true", help="print every point, not only deviations over the threshold")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    with serve() as base, sync_playwright() as p:
        browser = getattr(p, args.browser).launch()
        flagged = part_a(browser, base, args.browser, show_all=args.all)
        part_b(args.browser, flagged)
        part_c(browser, base)
        browser.close()


if __name__ == "__main__":
    main()
