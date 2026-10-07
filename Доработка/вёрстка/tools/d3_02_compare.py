"""Д3 · 02 «Вечер» A: сверка сайта с кадрами секции Figma 318:2377 (покой и наведение 02 на пяти проверочных окнах).

  python tools/d3_02_compare.py               # → сверка/d3_02/pair_<движок>_<окно>.png (сверху Figma, снизу сайт) + таблица
  python tools/d3_02_compare.py -b webkit

Кадры Figma — сверка/d3_02/02_w_<окно>_{r,h}.png, точки — из выгрузки сверка/d3_02/figma_tree.json (get_nodes_info
десяти кадров). Сайт — getBoundingClientRect от верха блока. Порог 4 px; x интенсивности не сравнивается
(Unbounded в Figma ~5 % шире веб-шрифта). Отдельно: блок = экран, раскрытая 02 и итог в экране, фото не наезжает на итог.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve, url_for
from pilot_shots import STILL, eager

OUT = SVERKA / "d3_02"
TREE = OUT / "figma_tree.json"
WINDOWS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
KINDS = {"r": 1, "h": 2}            # покой — раскрыта 01, наведение — 02

ROW = lambda n, part: f"Строка 0{n} · {part}"


def figma_points():
    frames = json.load(open(TREE, encoding="utf-8"))
    pts = {}
    for fi, fr in enumerate(frames):
        w, h = WINDOWS[fi // 2]
        kind = "rh"[fi % 2]
        assert f"{w}×{h}" in fr["name"], fr["name"]
        by = {c["name"]: c["bounds"] for c in fr["children"]}
        win = next(b for n, b in by.items() if n.startswith("Окно фото"))
        o = {"label": by["Номер секции"], "l1": by["Заголовок · 1"], "l2": by["Заголовок · 2"], "lead": by["Лид"],
             "photo": win, "big": by["Итог · крупно"], "note": by["Итог · капсом"]}
        n = KINDS[kind]
        for i in range(1, 6):
            o[f"line{i}"] = by[ROW(i, "линия")]
            o[f"name{i}"] = by[ROW(i, "название")]
            o[f"time{i}"] = by[ROW(i, "время")]
        o["dur"] = by[ROW(n, "длительность")]
        o["desc"] = by[ROW(n, "описание")]
        pts[f"{w}x{h}_{kind}"] = {k: [round(b["x"], 1), round(b["y"], 1)] for k, b in o.items()} | \
            {"photo_h": [0, round(win["height"], 1)]}
    return pts


SITE_JS = """() => {
  const s = document.querySelector('.s-evening'), top = s.getBoundingClientRect().top;
  const q = (sel, root = s) => root.querySelector(sel);
  const box = (el) => { const r = el.getBoundingClientRect(); return [r.left, r.top - top]; };
  const items = [...s.querySelectorAll('.eve__item')], on = q('.eve__item[data-on]');
  const ph = q('.eve__photo', on).getBoundingClientRect();
  const o = { label: box(q('.sh__label')), l1: box(q('.sh__l1')), l2: box(q('.sh__l2')), lead: box(q('.sh__lead')),
    photo: [ph.left, ph.top - top], photo_h: [0, ph.height], big: box(q('.eve__sum-1')), note: box(q('.eve__note')),
    dur: box(q('.eve__dur', on)), desc: [box(q('.eve__desc', on))[0], box(q('.eve__desc', on))[1] + parseFloat(getComputedStyle(q('.eve__desc', on), '::before').height)] };
  items.forEach((it, i) => { o['line' + (i + 1)] = box(it); o['name' + (i + 1)] = box(q('.eve__title', it)); o['time' + (i + 1)] = box(q('.eve__time', it)); });
  const H = s.getBoundingClientRect().height, sb = s.getBoundingClientRect().bottom;
  const last = items[items.length - 1].getBoundingClientRect().bottom;
  return { pts: o, check: { height: H, listBottom: last - top, finalBottom: q('.eve__final').getBoundingClientRect().bottom - top,
    photoGap: q('.eve__sum-1').getBoundingClientRect().top - ph.bottom, k: getComputedStyle(s).getPropertyValue('--k').trim(),
    descOpacity: getComputedStyle(q('.eve__desc', on)).opacity } };
}"""


def shoot(browser, base, w, h, engine):
    ctx = browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(url_for(base, "site/index.html"), wait_until="networkidle")
    eager(page)
    page.add_style_tag(content=STILL)
    top = page.evaluate("document.querySelector('#evening').getBoundingClientRect().top + scrollY")
    page.evaluate("y => scrollTo({top: y, behavior: 'instant'})", top)
    page.wait_for_timeout(300)
    files, meas = {}, {}
    for kind, n in KINDS.items():
        if n == 1:
            page.mouse.move(w - 5, h - 5)
        else:
            r = page.evaluate(f"document.querySelectorAll('.eve__item')[{n - 1}].getBoundingClientRect().toJSON()")
            page.wait_for_timeout(450)
            page.mouse.move(r["left"] + 300, r["top"] + 20)
            page.mouse.move(r["left"] + 310, r["top"] + 22)
        page.wait_for_timeout(400)
        f = OUT / f"site_{engine}_{w}x{h}_{kind}.png"
        page.screenshot(path=str(f))
        files[kind] = f
        meas[kind] = page.evaluate(SITE_JS)
    ctx.close()
    return files, meas


def pair_sheet(w, h, files, path, col_w=640):
    font = ImageFont.truetype("arial.ttf", 18)
    pad, head = 10, 26
    rows = [("Figma", [OUT / f"02_w_{w}x{h}_{k}.png" for k in KINDS]), ("Сайт", [files[k] for k in KINDS])]
    th = round(h * col_w / w)
    out = Image.new("RGB", (pad + 2 * (col_w + pad), pad + 2 * (head + th + pad)), (40, 40, 40))
    d = ImageDraw.Draw(out)
    y = pad
    for label, fs in rows:
        d.text((pad, y), f"{w}×{h} · {label} · покой | наведение 02", fill=(220, 215, 205), font=font)
        y += head
        for i, f in enumerate(fs):
            if f.exists():
                out.paste(Image.open(f).convert("RGB").resize((col_w, th), Image.LANCZOS), (pad + i * (col_w + pad), y))
        y += th + pad
    out.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    args = ap.parse_args()
    pts = figma_points()
    worst, fails = 0, 0
    with serve() as base, sync_playwright() as p:
        browser = getattr(p, args.browser).launch()
        for w, h in WINDOWS:
            files, meas = shoot(browser, base, w, h, args.browser)
            pair_sheet(w, h, files, OUT / f"pair_{args.browser}_{w}x{h}.png")
            for kind in KINDS:
                c = meas[kind]["check"]
                ok = abs(c["height"] - h) < 1 and c["listBottom"] <= h - 63 and c["finalBottom"] <= h - 63 and c["photoGap"] > 0 \
                    and float(c["descOpacity"]) == 1
                fails += not ok
                bad = []
                for k, (fx, fy) in pts[f"{w}x{h}_{kind}"].items():
                    sx, sy = meas[kind]["pts"][k]
                    dx, dy = (0 if k == "dur" else sx - fx), sy - fy
                    worst = max(worst, abs(dx), abs(dy))
                    if abs(dx) > 4 or abs(dy) > 4:
                        bad.append(f"{k} Δx {dx:+.1f} Δy {dy:+.1f}")
                fails += bool(bad)
                print(f"{'ok ' if ok and not bad else '!! '} {w}×{h} {kind} k {c['k']} · блок {c['height']:.0f} · низ списка "
                      f"{c['listBottom']:.1f} · низ итога {c['finalBottom']:.1f} · зазор фото {c['photoGap']:.1f}"
                      + ("" if not bad else " — " + "; ".join(bad)))
        browser.close()
    print(f"наибольшее отклонение {worst:.1f} px, кадров с ошибкой: {fails}")


if __name__ == "__main__":
    main()
