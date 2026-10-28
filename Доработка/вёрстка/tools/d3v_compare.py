# 11–footer part removed in Ц4 (2026-10-28): the finale is checked by c4_compare.py
"""Д3в и сжатые шапки: сверка 04, 09, 10 с кадрами Figma на проверочных окнах — картинкой и цифрами. 08 — снят в Ц2, сверка нового 08 — c2_compare.py.

  python tools/d3v_compare.py               # → сверка/d3v/pair_<движок>_<окно>.png (сверху Figma, снизу сайт) + таблица отклонений
  python tools/d3v_compare.py -b webkit
  python tools/d3v_compare.py --tree сверка/d3v/figma_tree.json   # пересобрать точки Figma из выгрузки 40 кадров

Кадры Figma: секция «Д3в · выбранное (09 A, 10 B, 11–подвал A) на проверочных окнах» (09, 10 — по два экрана) и
«Сжатые шапки · 04 / 08 на проверочных окнах».
Точки — левый верхний угол узла от верха своего экрана; шапки 04, 09, 10 не в экран — их высота
сверяется с высотой кадра, экраны тела (09 фигуры, 10 тело) — с высотой окна. Порог — 4 px.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve, url_for
from pilot_shots import STILL, eager

OUT = SVERKA / "d3v"
POINTS = OUT / "figma_points.json"
WINDOWS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
KINDS = ["04h", "09h", "09f", "10h", "10b"]
# имя кадра Figma по виду; 08 — снят в Ц2, сверка нового 08 — c2_compare.py
FRAME_NAME = {"04h": "Сжатые шапки · {w}×{h} · 04",
              "09h": "Д3в · {w}×{h} · 09 · экран 1", "09f": "Д3в · {w}×{h} · 09 · экран 2",
              "10h": "Д3в · {w}×{h} · 10 · экран 1", "10b": "Д3в · {w}×{h} · 10 · экран 2"}
HEADS = {"04h", "09h", "10h"}          # не в экран: сверяется высота кадра

PATHS = {
    "04h": {"label": ("Метка",), "l1": ("Заголовок",), "lead": ("Лид",)},
    "09h": {"label": ("Номер секции",), "l1": ("Заголовок — строка 1",), "l2": ("Заголовок — строка 2 (на оси)",), "intro": ("Интро",),
            "hl": ("Мы поможем · метка",), "sv1": ("Сервис 1",), "sv2": ("Сервис 2",), "sv3": ("Сервис 3",)},
    "09f": {"rk": ("Роль · Кавалерам",), "rd": ("Роль · Дамам",), "pk": ("Фото · Кавалер",), "pd": ("Фото · Дама",),
            "nk": ("Номер · Кавалерам",), "nd": ("Номер · Дамам",), "k1": ("К · Бабочка",), "k4": ("К · Туфли",),
            "d1": ("Д · Причёска",), "d4": ("Д · Обувь",), "w": ("Белый · слово",), "wc": ("Белый · продолжение",)},
    "10h": {"label": ("Метка",), "l1": ("Заголовок · 1",), "l2": ("Заголовок · 2",), "lead": ("Подзаголовок",)},
    "10b": {"count": ("Счётчик",), "t1": ("Пункт · Омега",), "t2": ("Пункт · Кашемир",), "sb": ("Слот B · Омега",),
            "sa": ("Слот A · Омега",), "sc": ("Слот C · Омега",), "sd": ("Слот D · Омега",), "win": ("Название",),
            "desc": ("Суть · Омега",), "fact": ("Цифра · Омега 1",)},
}

# Сайт: [селектор экрана, сдвиг верха экрана (JS-выражение от секции s), {точка: JS-выражение элемента}]
SITE_JS = """([kind]) => {
  const q = (s) => document.querySelector(s), qa = (s) => [...document.querySelectorAll(s)];
  const top = (el) => el.getBoundingClientRect().top + scrollY;
  const sec = { '04h': '#dancemaster', '09h': '#dresscode', '09f': '#dresscode',
                '10h': '#evenings', '10b': '#evenings' }[kind];
  const s = q(sec), st = top(s);
  const help = q('.dress__help'), sh10 = q('#evenings > .sh');
  const head = { '04h': q('#dancemaster > .sh').offsetHeight,
                 '09h': help.offsetTop + help.offsetHeight, '10h': sh10.offsetHeight };
  const y0 = st + ({ '09f': head['09h'], '10b': head['10h'] }[kind] || 0);
  const box = (el, dy = 0) => { const r = el.getBoundingClientRect(); return [r.left, r.top + scrollY - y0 + dy]; };
  const o = { y0 };
  if (kind in head) o.height = head[kind];
  if (kind === '09f' || kind === '10b') o.height = s.offsetHeight - (y0 - st);
  const sh = (p) => Object.assign({ label: box(q(p + ' .sh__label')), l1: box(q(p + ' .sh__l1')) }, q(p + ' .sh__l2') ? { l2: box(q(p + ' .sh__l2')) } : {});
  if (kind === '04h') Object.assign(o, sh('#dancemaster'), { lead: box(q('#dancemaster .sh__lead')) });
  else if (kind === '09h') {
    const sv = qa('.dress__svc li');
    Object.assign(o, sh('#dresscode'), { intro: box(q('.dress__intro')), hl: box(q('.dress__hl')), sv1: box(sv[0]), sv2: box(sv[1]), sv3: box(sv[2]) });
  } else if (kind === '09f') {
    const f = (r) => q(`.dress__fig[data-fig=${r}]`), rk = f('k').querySelectorAll('.dress__rule'), rd = f('d').querySelectorAll('.dress__rule');
    Object.assign(o, { rk: box(f('k').querySelector('.dress__role')), rd: box(f('d').querySelector('.dress__role')),
      pk: box(f('k').querySelector('.dress__photo')), pd: box(f('d').querySelector('.dress__photo')),
      nk: box(f('k').querySelector('.dress__num')), nd: box(f('d').querySelector('.dress__num')),
      k1: box(rk[0]), k4: box(rk[3]), d1: box(rd[0]), d4: box(rd[3]), w: box(q('.dress__w')), wc: box(q('.dress__wc')) });
  } else if (kind === '10h') Object.assign(o, sh('#evenings'), { lead: box(q('#evenings .sh__lead')) });
  else if (kind === '10b') {
    const sl = (k) => box(q(`.eves__slot[data-slot=${k}]`));
    Object.assign(o, { count: box(q('.eves__count')), t1: box(q('.eves__tab[data-i="1"] span')), t2: box(q('.eves__tab[data-i="2"] span')),
      sb: sl('b'), sa: sl('a'), sc: sl('c'), sd: sl('d'), win: box(q('.eves__win')),
      desc: box(q('#eves-p1 .eves__desc')), fact: box(q('#eves-p1 .eves__fn')) });
  }
  return o;
}"""


def build_points(tree):
    frames = json.load(open(tree, encoding="utf-8"))
    pts = {}
    for w, h in WINDOWS:
        for kind in KINDS:
            pre = FRAME_NAME[kind].format(w=w, h=h)
            fr = next(f for f in frames if f["name"].startswith(pre))
            out = {"height": round(fr["bounds"]["height"], 1)}
            for key, path in PATHS[kind].items():
                node, x, y = fr, 0, 0
                for nm in path:
                    node = next(c for c in node["children"] if c["name"] == nm)
                    x, y = x + node["bounds"]["x"], y + node["bounds"]["y"]
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
    for kind in KINDS:
        m = page.evaluate(SITE_JS, [kind])
        page.evaluate("y => scrollTo({top: y, behavior: 'instant'})", m["y0"])
        page.mouse.move(w / 2, 2)
        page.wait_for_timeout(300)
        m = page.evaluate(SITE_JS, [kind])
        f = OUT / f"site_{engine}_{w}x{h}_{kind}.png"
        page.screenshot(path=str(f))
        files[kind], meas[kind] = f, m
    ctx.close()
    return files, meas


def figma_png(w, kind):
    if kind in ("04h", "09h", "10h"):
        return SVERKA / "shrink" / f"{w}_{kind[:2]}.png"
    return OUT / "windows" / f"d3v_w_{w}_{kind}.png"


def pair_sheet(w, h, files, path, col_w=300):
    font = ImageFont.truetype("arial.ttf", 16)
    pad, head = 10, 24
    th = round(h * col_w / w)
    rows = [("Figma", [figma_png(w, k) for k in KINDS]), ("Сайт", [files[k] for k in KINDS])]
    out = Image.new("RGB", (pad + len(KINDS) * (col_w + pad), pad + len(rows) * (head + th + pad)), (40, 40, 40))
    d = ImageDraw.Draw(out)
    y = pad
    for label, fs in rows:
        d.text((pad, y), f"{w}×{h} · {label} · " + " | ".join(KINDS), fill=(220, 215, 205), font=font)
        y += head
        for i, f in enumerate(fs):
            if f.exists():
                im = Image.open(f).convert("RGB")
                im = im.resize((col_w, round(im.height * col_w / im.width)))
                out.paste(im.crop((0, 0, col_w, th)), (pad + i * (col_w + pad), y))
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
            for kind in KINDS:
                bad = []
                for k, fv in pts[f"{w}x{h}_{kind}"].items():
                    if k == "height":
                        d = meas[kind]["height"] - fv
                        worst = max(worst, abs(d))
                        if abs(d) > 4:
                            bad.append(f"высота {meas[kind]['height']:.0f} / {fv:.0f}")
                        continue
                    fx, fy = fv
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
