"""Д3б: сверка 06 «в экран» с кадрами секции Figma «Д3б · выбранное (06 A, 07 один экран, 08 A1) на проверочных окнах»
(328:3071) — картинкой и цифрами. 07 — снят в Ц3, сверка нового 07 — c3_compare.py; 08 — снят в Ц2, сверка нового 08 — c2_compare.py.

  python tools/d3b_compare.py               # → сверка/d3b/pair_<движок>_<окно>.png (сверху Figma, снизу сайт) + таблица отклонений
  python tools/d3b_compare.py -b webkit
  python tools/d3b_compare.py --tree <get_nodes_info.json>   # пересобрать точки Figma из выгрузки 25 кадров (порядок FRAMES)

Кадры Figma — сверка/d3b/windows/d3b_w_<ширина>_<вид>.png. Точки — сверка/d3b/figma_points.json: левый верхний угол узла от верха
экрана (у «Принципа» — левый нижний: текст прижат низом; 08 — снят в Ц2, сверка нового 08 — c2_compare.py). Сайт — getBoundingClientRect от верха того же экрана. Порог — 4 px.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve, url_for
from pilot_shots import STILL, eager

OUT = SVERKA / "d3b"
SHOTS = OUT / "windows"
POINTS = OUT / "figma_points.json"
WINDOWS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
KINDS = ["06", "06v"]  # 07 is no longer compared here (stage Ц3): its check is c3_compare.py
# 25 кадров Figma, по 5 на окно: 06, 06v, 07, 08h, 08p. 07 — снят в Ц3 (сверка — c3_compare.py), 08 — снят в Ц2, сверка нового 08 — c2_compare.py;
# шаг 5 в build_points оставлен, чтобы индексы совпадали с порядком кадров в Figma
FRAMES = ["328:3073", "328:3112", "328:3151", "328:3186", "328:3198", "328:3245", "328:3284", "328:3323", "328:3358", "328:3370",
          "328:3417", "328:3456", "328:3495", "328:3530", "328:3542", "328:3589", "328:3628", "328:3667", "328:3702", "328:3714",
          "328:3761", "328:3800", "328:3839", "328:3874", "328:3886"]

HEAD06 = {"label": ("Метка",), "l1": ("Заголовок · 1",), "l2": ("Заголовок · 2 на оси",), "lead": ("Лид",),
          "r1": ("Строка 01",), "r2": ("Строка 02",), "r3": ("Строка 03",), "q2": ("Строка 02", "Название"), "pr": ("Принцип",)}
PATHS = {
    "06": HEAD06 | {"ans": ("Ответ 01",), "photo": ("Кадр 01 Стесняетесь",)},
    "06v": HEAD06 | {"ans": ("Ответ 02",), "photo": ("Кадр 02 Не умеете танцевать",), "expl": ("Ответ 02", "Пояснение")},
}

SITE_JS = """([kind, sTop]) => {
  const q = (s) => document.querySelector(s), qa = (s) => [...document.querySelectorAll(s)];
  const box = (el) => { const r = el.getBoundingClientRect(); return [r.left, r.top - sTop]; };
  const o = {};
  if (kind === '06' || kind === '06v') {
    const s = '.s-assistant', it = qa('.asst__item'), on = q('.asst__item[data-on]');
    const pr = q('.asst__principle').getBoundingClientRect();
    Object.assign(o, { label: box(q(s + ' .sh__label')), l1: box(q(s + ' .sh__l1')), l2: box(q(s + ' .sh__l2')), lead: box(q(s + ' .sh__lead')),
      r1: box(it[0]), r2: box(it[1]), r3: box(it[2]), q2: box(it[1].querySelector('.asst__q')), pr: [pr.left, pr.bottom - sTop],
      ans: box(on.querySelector('.asst__a')), photo: box(on.querySelector('.asst__photo')) });
    if (kind === '06v') o.expl = box(on.querySelector('.asst__note'));
    o.tight = q(s).hasAttribute('data-tight');
  }
  return o;
}"""


def build_points(tree):
    frames = {f["id"]: f for f in json.load(open(tree, encoding="utf-8"))}
    pts = {}
    for wi, (w, h) in enumerate(WINDOWS):
        for ki, kind in enumerate(KINDS):
            fr = frames[FRAMES[wi * 5 + ki]]
            assert f"{w}×{h}" in fr["name"], fr["name"]
            out = {}
            for key, path in PATHS[kind].items():
                node, x, y = fr, 0, 0
                for nm in path:
                    node = next(c for c in node["children"] if c["name"] == nm)
                    x, y = x + node["bounds"]["x"], y + node["bounds"]["y"]
                if key == "pr":
                    y += node["bounds"]["height"]
                out[key] = [round(x, 1), round(y, 1)]
            pts[f"{w}x{h}_{kind}"] = out
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
    sec = {"06": "#assistant"}
    hs = page.evaluate("() => ['#assistant'].map(s => document.querySelector(s).getBoundingClientRect().height)")
    meas["heights"] = [round(x / h, 2) for x in hs]                     # ожидается 1; 07 — высота секции в c3_compare.py; 08 — снят в Ц2, сверка нового 08 — c2_compare.py
    for kind in KINDS:
        top = page.evaluate("s => document.querySelector(s).getBoundingClientRect().top + scrollY", sec[kind[:2]])
        page.evaluate("y => scrollTo({top: y, behavior: 'instant'})", top)
        page.mouse.move(w / 2, 2)
        if kind[:2] == "06":
            r = page.evaluate("i => document.querySelectorAll('.asst__q')[i].getBoundingClientRect().toJSON()", 1 if kind == "06v" else 0)
            page.mouse.move(r["left"] + 20, r["top"] + 10)
        page.wait_for_timeout(400)
        f = OUT / f"site_{engine}_{w}x{h}_{kind}.png"
        page.screenshot(path=str(f))
        files[kind] = f
        meas[kind] = page.evaluate(SITE_JS, [kind, 0])
    ctx.close()
    return files, meas


def pair_sheet(w, h, files, path, col_w=420):
    font = ImageFont.truetype("arial.ttf", 18)
    pad, head = 10, 26
    rows = [("Figma", [SHOTS / f"d3b_w_{w}_{k}.png" for k in KINDS]), ("Сайт", [files[k] for k in KINDS])]
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
    worst, fails = 0, 0
    with serve() as base, sync_playwright() as p:
        browser = getattr(p, args.browser).launch()
        for w, h in WINDOWS:
            files, meas = shoot(browser, base, w, h, args.browser)
            pair_sheet(w, h, files, OUT / f"pair_{args.browser}_{w}x{h}.png")
            tight = meas["06"]["tight"]
            okh = meas["heights"] == [1] and tight == (h < 900)
            fails += not okh
            print(f"{'ok ' if okh else '!! '} {w}×{h} высота 06 в экране {meas['heights']}, «Принцип» на фото: {tight}")
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
