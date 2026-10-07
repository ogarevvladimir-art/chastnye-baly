"""Д4: снимки сайта с заменёнными фото — каждый слот в своём состоянии блока на проверочных окнах.

    python tools/d4_shots.py              # → сверка/d4/site_<окно>.png (лист кадров)
    python tools/d4_shots.py -b webkit
"""
import argparse
import io

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve, url_for
from pilot_shots import STILL, eager

OUT = SVERKA / "d4"
WINDOWS = [(1440, 900), (1920, 950), (1366, 650), (390, 844), (834, 1194)]

# (подпись, селектор секции, сдвиг в экранах, JS состояния)
VIEWS = [("hero", ".s-hero", 0, ""),
         ("Форматы · корп.", "#formats", 0, "s.dataset.state='corporate'"),
         *[(f"02 · {i}", "#evening", 0,
            f"s.querySelectorAll('.eve__item').forEach((it,k)=>it.toggleAttribute('data-on',k=={i - 1}))") for i in range(1, 6)],
         ("03 · духовой", "#music", 0, "s.dataset.state='2'"),
         ("03 · группа", "#music", 0, "s.dataset.state='3'"),
         ("04 · зрители", "#dancemaster", 1, "s.dataset.state='spectators'"),
         ("04 · участники", "#dancemaster", 1, "s.dataset.state='participants'"),
         *[(f"05 · {i}", "#show", f, "") for i, f in ((1, .15), (2, .5), (3, .85))],
         ("07 · панорама", "#lessons", 0, "")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--browser", default="chromium")
    args = ap.parse_args()
    font = ImageFont.truetype("arial.ttf", 22)
    with serve() as base, sync_playwright() as p:
        b = getattr(p, args.browser).launch()
        for w, h in WINDOWS:
            ctx = b.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
            pg = ctx.new_page()
            pg.goto(url_for(base, "site/index.html"), wait_until="networkidle")
            pg.add_style_tag(content=STILL)
            eager(pg)
            shots = []
            for label, sel, screens, js in VIEWS:
                if label.startswith("07"):
                    # панорама — по самому фото
                    pg.evaluate("""() => { const i = document.querySelector('#lessons picture img');
                        const r = i.getBoundingClientRect(); scrollTo({top: scrollY + r.top + r.height / 2 - innerHeight / 2, behavior: 'instant'}); }""")
                elif label.startswith("05"):
                    # закреплённая сцена: доля прокрутки внутри секции
                    pg.evaluate(f"""() => {{ const s = document.querySelector('{sel}'), r = s.getBoundingClientRect();
                        scrollTo({{top: r.top + scrollY + {screens} * Math.max(0, r.height - innerHeight), behavior: 'instant'}}); }}""")
                    pg.wait_for_timeout(400)
                else:
                    pg.evaluate(f"""() => {{ const s = document.querySelector('{sel}');
                        scrollTo({{top: s.getBoundingClientRect().top + scrollY + {screens} * innerHeight, behavior: 'instant'}});
                        {js}; }}""")
                eager(pg)
                pg.wait_for_timeout(250)
                im = Image.open(io.BytesIO(pg.screenshot()))
                ImageDraw.Draw(im).text((12, h - 40), label, fill=(255, 255, 0), font=font)
                shots.append(im)
            ctx.close()
            cols = 4 if w > 900 else 8
            tw = 720 if w > 900 else 300
            th = round(tw * h / w)
            rows = (len(shots) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * (tw + 8), rows * (th + 8)), "white")
            for i, im in enumerate(shots):
                sheet.paste(im.resize((tw, th), Image.LANCZOS), ((i % cols) * (tw + 8), (i // cols) * (th + 8)))
            sheet.save(OUT / f"site_{args.browser}_{w}x{h}.png")
            print(w, h, "ok")
        b.close()


if __name__ == "__main__":
    main()
