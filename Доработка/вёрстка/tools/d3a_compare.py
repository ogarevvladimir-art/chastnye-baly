"""Д3а: сверка 01, 03, 04 «в экран» с кадрами секции Figma 307:2595 на проверочных окнах — картинкой и цифрами.

  python tools/d3a_compare.py               # → сверка/d3a/pair_<движок>_<окно>.png (сверху Figma, снизу сайт) + таблица отклонений
  python tools/d3a_compare.py -b webkit
  python tools/d3a_compare.py --tree <get_nodes_info.json>   # пересобрать точки Figma из выгрузки 35 кадров

Кадры Figma — .figma-shots/d3w_<ширина>_<вид>.png. Точки — сверка/d3a/figma_points.json (левый верхний угол узла
от верха экрана). Сайт — getBoundingClientRect (у описаний — без padding) от верха того же экрана. Порог — 4 px.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve, url_for
from pilot_shots import STILL, eager

SHOTS = Path(r"C:\Users\ogare\Desktop\Мои документы\VS CODE\.figma-shots")
OUT = SVERKA / "d3a"
POINTS = OUT / "figma_points.json"
WINDOWS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
KINDS = ["01h", "01r", "01v", "03", "04h", "04r", "04v"]

# Узлы Figma по виду кадра: ключ → путь имён от кадра
ROWS = ["Шаг 01 · Разговор", "Шаг 02 · Концепция", "Шаг 03 · Репетиции", "Шаг 04 · Вечер", "Шаг 05 · Воспоминания"]
STEPS = {f"w{i + 1}": ("Шаги", r, "Слово") for i, r in enumerate(ROWS)} | {f"n{i + 1}": ("Шаги", r, "Номер") for i, r in enumerate(ROWS)}
STEPS["end"] = ("Шаги", "Линия низ")
SCENE = {"scene": ("Сцена",), "quote": ("Цитата",), "tempo": ("Абзац · темп",), "p2": ("Сцена", "Панель / Участники"),
         "sw1": ("Сцена", "Панель / Зрители", "Слово"), "sn1": ("Сцена", "Панель / Зрители", "Номер"),
         "sw2": ("Сцена", "Панель / Участники", "Слово"), "sn2": ("Сцена", "Панель / Участники", "Номер")}
PATHS = {
    "01h": {"label": ("Номер секции",), "l1": ("Заголовок · 1",), "l2": ("Заголовок · 2 на оси",), "lead": ("Лид · от оси",),
            "photo": ("Фото · nk-05",)},
    "01r": STEPS,
    "01v": STEPS | {"d1": ("Шаги", ROWS[0], "Описание")},
    "03": {"label": ("Метка",), "l1": ("Заголовок · 1",), "l2": ("Заголовок · 2 лесенкой",), "lead": ("Лид",),
           "photo": ("Фото 01 Симфонический",), "tone": ("Тон · под колонками",),
           "c1": ("Формат 01",), "c2": ("Формат 02",), "c3": ("Формат 03",),
           "t1": ("Формат 01", "Название"), "t3": ("Формат 03", "Название"), "dn1": ("Формат 01", "Танцы"), "d1": ("Формат 01", "Описание")},
    "04h": {"label": ("Метка",), "title": ("Заголовок",), "lead": ("Лид",)},
    "04r": SCENE,
    "04v": SCENE | {"x2": ("Сцена", "Панель / Участники", "Абзац")},
}

# Сайт: тот же ключ → [x, y] от верха экрана (sTop — верх экрана в окне)
SITE_JS = """([kind, sTop]) => {
  const q = (s) => document.querySelector(s), qa = (s) => [...document.querySelectorAll(s)];
  const box = (el) => { const r = el.getBoundingClientRect(); return [r.left, r.top - sTop]; };
  const inner = (el) => { const r = el.getBoundingClientRect(), c = getComputedStyle(el);
    return [r.left + parseFloat(c.paddingLeft), r.top + parseFloat(c.paddingTop) - sTop]; };
  const o = {};
  if (kind[0] + kind[1] === '01') {
    if (kind === '01h') Object.assign(o, { label: box(q('.s-prep .sh__label')), l1: box(q('.s-prep .sh__l1')), l2: box(q('.s-prep .sh__l2')), lead: box(q('.s-prep .sh__lead')), photo: box(q('.prep__photo')) });
    else {
      // номер — по зазору от конца слова (веб-Unbounded на ~5 % уже, чем в Figma: абсолютный x номера не сравнивается)
      qa('.prep__step').forEach((st, i) => { const w = st.querySelector('.prep__word'), n = st.querySelector('.prep__num');
        o['w' + (i + 1)] = box(w); o['n' + (i + 1)] = [n.getBoundingClientRect().left - w.getBoundingClientRect().right, box(n)[1]]; });
      const last = qa('.prep__step').pop().getBoundingClientRect();
      o.end = [0, last.bottom - 1 - sTop];
      o.d1 = inner(q('.prep__desc'));
    }
  } else if (kind === '03') {
    const c = qa('.music__card');
    Object.assign(o, { label: box(q('.s-music .sh__label')), l1: box(q('.s-music .sh__l1')), l2: box(q('.s-music .sh__l2')), lead: box(q('.s-music .sh__lead')),
      photo: box(q('.music__scene')), tone: [0, q('.music__rail').getBoundingClientRect().top + parseFloat(getComputedStyle(q('.music__rail'), '::before').top) - sTop],
      c1: box(c[0]), c2: box(c[1]), c3: box(c[2]), t1: box(c[0].querySelector('.music__title')), t3: box(c[2].querySelector('.music__title')),
      dn1: box(c[0].querySelector('.music__dances')), d1: box(c[0].querySelector('.music__desc')) });
  } else if (kind === '04h') {
    Object.assign(o, { label: box(q('.s-dancemaster .sh__label')), title: box(q('.s-dancemaster .sh__l1')), lead: box(q('.s-dancemaster .sh__lead')) });
  } else {
    const p = (n, s) => box(q(`[data-panel=${n}] ${s}`));
    const st = q('.dm__stage'), r2 = q('[data-panel=participants]');
    const l2 = parseFloat(getComputedStyle(r2).clipPath.match(/[0-9.]+px/g).pop());
    Object.assign(o, { scene: box(st), quote: box(q('.dm__quote')), tempo: box(q('.dm__tempo')),
      p2: [st.getBoundingClientRect().left + l2, st.getBoundingClientRect().top - sTop],
      sw1: p('spectators', '.dm__word'), sn1: p('spectators', '.dm__num'), sw2: p('participants', '.dm__word'), sn2: p('participants', '.dm__num'),
      x2: p('participants', '.dm__text') });
  }
  return o;
}"""


def build_points(tree):
    frames = json.load(open(tree, encoding="utf-8"))
    pts = {}
    for wi, (w, h) in enumerate(WINDOWS):
        for ki, kind in enumerate(KINDS):
            fr = frames[wi * 7 + ki]
            assert f"{w}×{h}" in fr["name"], fr["name"]
            out = {}
            for key, path in PATHS[kind].items():
                node, x, y = fr, 0, 0
                for nm in path:
                    parent = node
                    node = next(c for c in node["children"] if c["name"] == nm)
                    x, y = x + node["bounds"]["x"], y + node["bounds"]["y"]
                if kind[:2] == "01" and key[0] == "n" and key[1:].isdigit():
                    word = next(c for c in parent["children"] if c["name"] == "Слово")
                    x = node["bounds"]["x"] - word["bounds"]["x"] - word["bounds"]["width"]   # зазор от конца слова
                out[key] = [round(x, 1), round(y, 1)]
            pts[f"{w}x{h}_{kind}"] = out
    OUT.mkdir(parents=True, exist_ok=True)
    POINTS.write_text(json.dumps(pts, ensure_ascii=False, indent=1), encoding="utf-8")
    return pts


def shoot(browser, base, w, h, engine):
    ctx = browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(url_for(base, "site/index.html"), wait_until="networkidle")
    eager(page)
    page.add_style_tag(content=STILL)
    page.wait_for_timeout(300)
    files, meas = {}, {}
    sec = {"01": "#prep", "03": "#music", "04": "#dancemaster"}
    hs = page.evaluate("() => ['#prep', '#music', '#dancemaster'].map(s => document.querySelector(s).getBoundingClientRect().height)")
    head04 = page.evaluate("() => document.querySelector('#dancemaster > .sh').offsetHeight")   # шапка 04 не в экран (правка 2026-10-06)
    hs[2] -= head04
    meas["heights"] = [round(x / h, 2) for x in hs]                     # ожидается 2 / 1 / шапка + 1 экран
    for kind in KINDS:
        top = page.evaluate("s => document.querySelector(s).getBoundingClientRect().top + scrollY", sec[kind[:2]])
        if kind[2:] in ("r", "v"):
            top += h if kind[:2] == "01" else head04
        page.evaluate("y => scrollTo({top: y, behavior: 'instant'})", top)
        page.mouse.move(w / 2, 2)
        for s in ("#prep .prep__list", "#dancemaster .dm__stage"):
            page.evaluate("s => document.querySelector(s).dispatchEvent(new PointerEvent('pointerleave', {pointerType: 'mouse'}))", s)
        if kind == "01v":
            r = page.evaluate("document.querySelector('.prep__step').getBoundingClientRect().toJSON()")
            page.mouse.move(r["left"] + 200, r["top"] + 40)
        if kind == "04v":
            r = page.evaluate("document.querySelector('.dm__stage').getBoundingClientRect().toJSON()")
            page.mouse.move(r["left"] + r["width"] * 0.85, r["top"] + r["height"] / 2)
        page.wait_for_timeout(300)
        f = OUT / f"site_{engine}_{w}x{h}_{kind}.png"
        page.screenshot(path=str(f))
        files[kind] = f
        meas[kind] = page.evaluate(SITE_JS, [kind, 0])
        if kind == "01v":   # самое длинное раскрытие — в экране
            meas["fit01"] = page.evaluate("() => document.querySelector('.prep__step:last-child').getBoundingClientRect().bottom") <= h
    ctx.close()
    return files, meas


def pair_sheet(w, h, files, path, col_w=420):
    font = ImageFont.truetype("arial.ttf", 18)
    pad, head = 10, 26
    rows = [("Figma", [SHOTS / f"d3w_{w}_{k}.png" for k in KINDS]), ("Сайт", [files[k] for k in KINDS])]
    th = round(h * col_w / w)
    out = Image.new("RGB", (pad + len(KINDS) * (col_w + pad), pad + len(rows) * (head + th + pad)), (40, 40, 40))
    d = ImageDraw.Draw(out)
    y = pad
    for label, fs in rows:
        d.text((pad, y), f"{w}×{h} · {label} · " + " | ".join(KINDS), fill=(220, 215, 205), font=font)
        y += head
        for i, f in enumerate(fs):
            if f.exists():
                out.paste(Image.open(f).convert("RGB").resize((col_w, th)), (pad + i * (col_w + pad), y))
        y += th + pad
    out.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    ap.add_argument("--tree")
    args = ap.parse_args()
    pts = build_points(args.tree) if args.tree else json.loads(POINTS.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    worst, fails = 0, 0
    with serve() as base, sync_playwright() as p:
        browser = getattr(p, args.browser).launch()
        for w, h in WINDOWS:
            files, meas = shoot(browser, base, w, h, args.browser)
            pair_sheet(w, h, files, OUT / f"pair_{args.browser}_{w}x{h}.png")
            okh = meas["heights"] == [2, 1, 1] and meas["fit01"]
            fails += not okh
            print(f"{'ok ' if okh else '!! '} {w}×{h} высоты 01 / 03 / 04 (без шапки) в экранах {meas['heights']}, раскрытая 01 в экране: {meas['fit01']}")
            for kind in KINDS:
                bad = []
                for k, (fx, fy) in pts[f"{w}x{h}_{kind}"].items():
                    sx, sy = meas[kind][k]
                    dx, dy = sx - fx, sy - fy
                    worst = max(worst, abs(dx), abs(dy))
                    if abs(dx) > 4 or abs(dy) > 4:
                        bad.append(f"{k} Δx {dx:+.1f} Δy {dy:+.1f}")
                fails += bool(bad)
                print(f"{'ok ' if not bad else '!! '} {w}×{h} {kind:4}" + ("" if not bad else " — " + "; ".join(bad)))
        browser.close()
    print(f"наибольшее отклонение {worst:.1f} px, кадров с отклонением > 4 px: {fails}")


if __name__ == "__main__":
    main()
