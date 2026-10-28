"""Блок 08 «Этикет» (#etiquette): сверка с кадрами Figma — цифры, пары картинок и подгонка под окно.

  python tools/c2_compare.py              # chromium: часть A (таблицы и итог), B (пары), C (окна)
  python tools/c2_compare.py -b webkit
  python tools/c2_compare.py --all        # часть A: все точки, не только отклонения > 4 px

Часть A — точки кадров Figma против сайта, порог 4 px: x и y — всегда, h — где указана, w — у нетекстовых точек
(фото, половины). Ширина текста печатается со звёздочкой и в порог не входит. Часть B — пара «Figma | сайт» только
для кадров с отклонением > 4 px → сверка/ц2/pair_<движок>_<390|834|1440|1440f>.png. Часть C — окна 1440x900 … 1024x650
(половины, отступы, финал, p1) и ширины 360 … 1920 без горизонтального скролла.
Кадры Figma — из папки плагина figma-mcp-express (путь зашит в плагине).
"""
import argparse
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve, url_for
from pilot_shots import STILL, eager

TOOLS = Path(__file__).resolve().parent
OUT = SVERKA / "ц2"
FIGMA_DIR = Path("C:/Users/ogare/Desktop/Мои документы/VS CODE/.figma-shots")
THRESH = 4
REF_SEL = {"section": "#etiquette", "final": ".etq__final"}      # от чего отсчитывается y точки
# кадр: (ширина, высота окна, номер кадра Figma, снимок Figma, отсчёт y)
FRAMES = {
    "390": (390, 844, "392:3450", "c2s3-m.png", "section"),
    "834": (834, 1194, "392:3501", "c2s3-t.png", "section"),
    "1440": (1440, 900, "392:2940", "c2s3-d-rest.png", "section"),
    "1440f": (1440, 900, "392:2958", "c2s3-d-final.png", "final"),
}
HIDE = ".site-header,.skip{visibility:hidden!important}"          # шапка и пропуск к содержимому — не в кадре Figma
WINDOWS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
WIDTHS = [360, 390, 600, 834, 1023, 1024, 1280, 1440, 1920]
HEAD = f"{'точка':<8} {'Figma':<22} {'сайт':<30} {'dx':>7} {'dy':>7} {'dw':>7} {'dh':>7}  флаг"


def T(key, sel, x=None, y=None, w=None, h=None, mode="range"):
    """Текстовая точка: x (и w — только для информации) по DOM Range; y и h — по коробке элемента.
    mode: range — весь текст элемента; first — первый текстовый узел (p1 на телефоне); box — коробка (em)."""
    return {"key": key, "sel": sel, "mode": mode, "text": True, "fig": {"x": x, "y": y, "w": w, "h": h}}


def B(key, sel, x=None, y=None, w=None, h=None):
    """Нетекстовая точка (фото, половины, секция, финал): всё по коробке элемента."""
    return {"key": key, "sel": sel, "mode": "box", "text": False, "fig": {"x": x, "y": y, "w": w, "h": h}}


# точки Figma (левый верхний угол узла от левого края страницы и от верха отсчёта), по кадрам
ROWS = {
    "390": [
        B("section", "#etiquette", h=1922),
        T("label", ".etq__label", 16, 64),
        T("giant", ".etq__giant", 16, 96, w=227, h=38),
        T("intro", ".etq__intro", 16, 166),
        T("numK", "[data-half=k] .etq__num", 16, 276),
        T("whomK", "[data-half=k] .etq__whom", 56, 276),
        T("rulesK", "[data-half=k] .etq__rules", 16, 308),
        B("photoK", "[data-half=k] .etq__photo", 16, 372, 358, 448),
        B("halfD", "[data-half=d]", y=884),
        T("numD", "[data-half=d] .etq__num", 16, 948),
        T("whomD", "[data-half=d] .etq__whom", 56, 948),
        T("rulesD", "[data-half=d] .etq__rules", 16, 980),
        B("photoD", "[data-half=d] .etq__photo", 16, 1060, 358, 448),
        B("final", ".etq__final", y=1572),
        T("p1", ".etq__p1", 16, 1636, mode="first"),
        T("em", ".etq__p1 em", 66, 1678, mode="box"),
        T("p2", ".etq__p2", 117, 1720),
        T("cont", ".etq__cont", 195, 1794),
    ],
    "834": [
        B("section", "#etiquette", h=2330),
        T("label", ".etq__label", 32, 96),
        T("intro", ".etq__intro", 417, 96),
        T("giant", ".etq__giant", 32, 182, h=78),
        T("numK", "[data-half=k] .etq__num", 32, 324),
        T("whomK", "[data-half=k] .etq__whom", 72, 323),
        T("rulesK", "[data-half=k] .etq__rules", 417, 364),
        B("photoK", "[data-half=k] .etq__photo", 32, 440, 770, 520),
        B("halfD", "[data-half=d]", y=1024),
        T("numD", "[data-half=d] .etq__num", 32, 1120),
        T("whomD", "[data-half=d] .etq__whom", 72, 1119),
        T("rulesD", "[data-half=d] .etq__rules", 417, 1160),
        B("photoD", "[data-half=d] .etq__photo", 32, 1260, 770, 520),
        B("final", ".etq__final", y=1844),
        T("p1", ".etq__p1", 32, 1972),
        T("p2", ".etq__p2", 328, 2049),
        T("cont", ".etq__cont", 417, 2166),
    ],
    "1440": [
        B("rest", ".etq__rest", 0, 0, 1440, 900),          # половины на десктопе — display: contents, фон — градиент .etq__rest
        T("label", ".etq__label", 64, 104),
        T("giant", ".etq__giant", 64, 176, h=170),
        T("intro", ".etq__intro", 784, 104),
        T("numK", "[data-half=k] .etq__num", 64, 432),
        T("whomK", "[data-half=k] .etq__whom", 128, 432),
        T("rulesK", "[data-half=k] .etq__rules", 64, 472),
        T("numD", "[data-half=d] .etq__num", 784, 432),
        T("whomD", "[data-half=d] .etq__whom", 848, 432),
        T("rulesD", "[data-half=d] .etq__rules", 784, 472),
        B("photoK", "[data-half=k] .etq__photo", 0, 560, 720, 340),
        B("photoD", "[data-half=d] .etq__photo", 720, 560, 720, 340),
    ],
    "1440f": [
        B("final", ".etq__final", h=640),
        T("p1", ".etq__p1", 64, 157),
        T("p2", ".etq__p2", 400, 295),
        T("cont", ".etq__cont", 720, 447),
    ],
}

# замер точек: x — по коробке (нетекст, em) или по Range (текст; p1 на телефоне — по первому текстовому узлу);
# y и h — по коробке элемента; всё в координатах страницы относительно верха отсчёта
MEASURE = """([rows, refSel]) => {
  const refTop = document.querySelector(refSel).getBoundingClientRect().top + scrollY;
  const out = {};
  for (const r of rows) {
    const el = document.querySelector(r.sel);
    if (!el) { out[r.key] = null; continue; }
    const b = el.getBoundingClientRect();
    let x = b.left + scrollX, w = b.width;
    if (r.mode !== 'box') {
      const node = r.mode === 'first'
        ? ([...el.childNodes].find(n => n.nodeType === 3 && n.textContent.trim()) || el) : el;
      const g = document.createRange();
      g.selectNodeContents(node);
      const rr = g.getBoundingClientRect();
      x = rr.left + scrollX;
      w = rr.width;
    }
    out[r.key] = { x: x, y: b.top + scrollY - refTop, w: w, h: b.height };
  }
  return out;
}"""

# замер части C одним вызовом (координаты окна при секции у верха окна)
MEASURE_C = """() => {
  const q = (s) => document.querySelector(s);
  const R = (el) => { const r = el.getBoundingClientRect(); return { l: r.left, r: r.right, t: r.top, b: r.bottom, h: r.height }; };
  const g = document.createRange();
  g.selectNodeContents(q('.etq__p1'));
  return {
    iw: innerHeight, cw: document.documentElement.clientWidth,
    halfK: R(q('.etq__rest')), halfD: R(q('.etq__rest')),
    giant: R(q('.etq__giant')), intro: R(q('.etq__intro')),
    whoK: R(q('[data-half=k] .etq__who')), whoD: R(q('[data-half=d] .etq__who')),
    photoK: R(q('[data-half=k] .etq__photo')), photoD: R(q('[data-half=d] .etq__photo')),
    picK: R(q('[data-half=k] .etq__photo picture')), picD: R(q('[data-half=d] .etq__photo picture')),
    final: R(q('.etq__final')), cont: R(q('.etq__cont')),
    p1r: g.getBoundingClientRect().right
  };
}"""
SW = "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"


def open_page(browser, base, w, h):
    """Страница сайта для сверки: без анимаций (STILL), ленивые картинки загружены, шрифты готовы, +300 мс."""
    ctx = browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(url_for(base, "site/index.html"), wait_until="networkidle")
    page.add_style_tag(content=STILL)
    eager(page)
    page.wait_for_timeout(300)
    return ctx, page


def scroll_to(page, sel, dy=0, wait=300):
    """Верх элемента — к верху окна (dy — сдвиг), прокрутка мгновенная."""
    top = page.evaluate("s => document.querySelector(s).getBoundingClientRect().top + scrollY", sel)
    page.evaluate("y => scrollTo({top: y, behavior: 'instant'})", top + dy)
    page.wait_for_timeout(wait)


def take_shot(page, key, path):
    """Снимок сайта под пару: телефон и планшет — #etiquette целиком; десктоп — окно от верха секции;
    финал — коробка .etq__final (1440x640). Шапка скрыта через visibility, вёрстку не меняет."""
    page.add_style_tag(content=HIDE)
    if key == "1440":
        scroll_to(page, "#etiquette")
        page.screenshot(path=str(path))
    elif key == "1440f":
        page.locator(".etq__final").screenshot(path=str(path))
    else:
        page.locator("#etiquette").screenshot(path=str(path))


def compare(r, m):
    """Строка таблицы по одной точке: (строка, есть отклонение > 4 px, наибольшее посчитанное отклонение)."""
    fig, name = r["fig"], r["key"]
    if m is None:
        return f"{name:<8} нет элемента: {r['sel']}", True, 0.0
    given = [f for f in ("x", "y", "w", "h") if fig[f] is not None]
    cells, bad, worst = {}, False, 0.0
    for f in given:
        d = m[f] - fig[f]
        info = f == "w" and r["text"]                  # ширина текста — только для информации
        cells[f] = f"{d:+.1f}" + ("*" if info else "")
        if not info:
            worst = max(worst, abs(d))
            bad = bad or abs(d) > THRESH
    fig_s = " ".join(f"{f}{fig[f]:g}" for f in given)
    site_s = " ".join(f"{f}{m[f]:.1f}" for f in given)
    dcol = " ".join(f"{cells.get(f, ''):>7}" for f in ("x", "y", "w", "h"))
    return f"{name:<8} {fig_s:<22} {site_s:<30} {dcol}  {'>4' if bad else ''}", bad, worst


def part_a(browser, base, engine, show_all=False):
    """Часть A: таблица на кадр и итог. Возвращает кадры с отклонением > 4 px и их снимки сайта (для части B)."""
    worst, flagged, shots = 0.0, [], {}
    for key, (w, h, name, _, ref) in FRAMES.items():
        ctx, page = open_page(browser, base, w, h)
        meas = page.evaluate(MEASURE, [ROWS[key], REF_SEL[ref]])
        bad_n, fw, lines = 0, 0.0, []
        for r in ROWS[key]:
            line, bad, rw = compare(r, meas[r["key"]])
            lines.append((line, bad))
            bad_n += bad
            fw = max(fw, rw)
        shown = [line for line, bad in lines if show_all or bad]
        if shown:
            print(f"\n{engine} · {w}x{h} · кадр Figma {name}")
            print(HEAD)
            for line in shown:
                print(line)
            print(f"  кадр: наибольшее отклонение {fw:.1f} px, точек > 4 px: {bad_n}")
        else:
            print(f"{engine} · {w}x{h} · кадр Figma {name}: ok (≤{THRESH} px)")
        worst = max(worst, fw)
        if bad_n:
            flagged.append(key)
            shots[key] = OUT / f"site_{engine}_{key}.png"
            take_shot(page, key, shots[key])
        ctx.close()
    print("* ширина текста: только для информации, в порог не входит")
    print(f"\nнаибольшее отклонение {worst:.1f} px, кадров > 4 px: {len(flagged)}")
    return flagged, shots


def part_b(engine, flagged, shots):
    """Часть B: пары «Figma | сайт» — только для кадров с отклонением > 4 px."""
    print("\nчасть B — пары «Figma | сайт»:")
    if not flagged:
        print("  кадров с отклонением > 4 px нет — пары не собираются")
    for key in flagged:
        fig = FIGMA_DIR / FRAMES[key][3]
        if not fig.exists():
            print(f"  нет снимка Figma: {fig}")
            continue
        out = OUT / f"pair_{engine}_{key}.png"
        subprocess.run([sys.executable, str(TOOLS / "pair.py"), str(fig), str(shots[key]), "-o", str(out)],
                       check=True, stdout=subprocess.DEVNULL)
        print(f"  {key}: {out}")


def fit_checks(m, w, h):
    """Проверки части C по замеру одного окна: (заголовок, [(ок, текст), ...])."""
    iw, cw = m["iw"], m["cw"]
    u = (min(cw, 1920) - 128) / 1312
    s = min(u, iw / 900)
    exp = round(640 * s)
    hk, hd = m["halfK"]["h"], m["halfD"]["h"]
    gi, it = m["giant"], m["intro"]
    wk, wd, pk, pd = m["whoK"], m["whoD"], m["photoK"], m["photoD"]
    ik, idd, fi, co = m["picK"], m["picD"], m["final"], m["cont"]
    gk, gd = wk["t"] - gi["b"], wd["t"] - gi["b"]              # зазор giant → who
    cap = gi["t"] + 0.2 * gi["h"]                               # верх глифов giant (0.2 высоты коробки ниже её верха)
    gint = cap - it["b"]                                        # зазор intro → giant
    ak, ad = pk["t"] - wk["b"], pd["t"] - wd["b"]               # зазор who → photo
    mk = [pk["l"] - ik["l"], ik["r"] - pk["r"], pk["t"] - ik["t"], ik["b"] - pk["b"]]
    md = [pd["l"] - idd["l"], idd["r"] - pd["r"], pd["t"] - idd["t"], idd["b"] - pd["b"]]
    gc = fi["b"] - co["b"]                                      # зазор cont → низ финала
    gp = cw - 16 - m["p1r"]                                     # запас p1 до правого края окна

    def fmt(xs):
        return " ".join(f"{v:.1f}" for v in xs)

    head = f"окно {w}x{h}: innerHeight {iw}, clientWidth {cw}, u {u:.3f}, s {s:.3f}, высота финала {exp} ±1"
    res = [
        (abs(hk - iw) <= 1 and abs(hd - iw) <= 1,
         f"1 .etq__rest (покой), высота {hk:.1f} при окне {iw} (±1)"),
        (gk > 0 and gd > 0 and gint >= 0,
         f"2 giant низ {gi['b']:.1f}: зазор до who k {gk:.1f}, d {gd:.1f} (>0); "
         f"intro низ {it['b']:.1f}, верх глифов giant {cap:.1f}: зазор {gint:.1f} (>=0)"),
        (ak >= 8 and ad >= 8,
         f"3 who низ до photo верх: зазор k {ak:.1f}, d {ad:.1f} (>=8)"),
        (all(v >= -1 for v in mk + md),
         f"4 picture содержит photo, запас слева/справа/сверху/снизу: k {fmt(mk)}; d {fmt(md)} (>=-1)"),
        (abs(fi["h"] - exp) <= 1,
         f"5a .etq__final высота {fi['h']:.1f}, ожидание round(640*s) = {exp} (±1)"),
        (gc >= 16,
         f"5b cont низ {co['b']:.1f}, низ финала {fi['b']:.1f}: зазор {gc:.1f} (>=16)"),
        (gp >= 0,
         f"5c p1 правый край (Range) {m['p1r']:.1f}, cw-16 = {cw - 16}: запас {gp:.1f} (>=0)"),
    ]
    return head, res


def part_c(browser, base):
    """Часть C: окна (верх секции у верха окна) и ширины без горизонтального скролла."""
    checks = fails = 0
    print("\nчасть C — подгонка под окно (верх секции у верха окна):")
    for w, h in WINDOWS:
        ctx, page = open_page(browser, base, w, h)
        scroll_to(page, "#etiquette")
        m = page.evaluate(MEASURE_C)
        ctx.close()
        head, res = fit_checks(m, w, h)
        print(head)
        for ok, text in res:
            checks += 1
            fails += not ok
            print(f"  {'ok  ' if ok else 'FAIL'} {text}")
    print("\nгоризонтальный скролл, высота 900: scrollWidth - clientWidth у #etiquette, затем от блока -200 через 250 мс:")
    for w in WIDTHS:
        ctx, page = open_page(browser, base, w, 900)
        scroll_to(page, "#etiquette")
        a = page.evaluate(SW)
        scroll_to(page, "#etiquette", dy=-200, wait=250)
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
        flagged, shots = part_a(browser, base, args.browser, show_all=args.all)
        part_b(args.browser, flagged, shots)
        part_c(browser, base)
        browser.close()


if __name__ == "__main__":
    main()
