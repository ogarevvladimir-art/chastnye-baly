"""og.jpg 1200 × 630 — карточка для соцсетей: миниатюра hero (фото в тоне, затемнение, логотип, «Частные» + БАЛЫ).

Фото — мастер hero-arch-d (build_photos.py), шрифты и логотип — из site/. Рендер — Chromium (Playwright).

    python og.py       # → site/og.jpg + сверка/логотип/v1_og.png
"""
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
SITE = PROJECT / "site"
MASTER = HERE / ".cache" / "masters" / "hero-arch-d.png"
W, H = 1200, 630

HTML = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Unbounded; src: url("{(SITE / 'fonts/unbounded-regular.woff2').as_uri()}") format("woff2"); font-weight: 400; }}
@font-face {{ font-family: Unbounded; src: url("{(SITE / 'fonts/unbounded-bold.woff2').as_uri()}") format("woff2"); font-weight: 700; }}
html, body {{ margin: 0; background: #060606; }}
.og {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; color: #c6c2b6; font-family: Unbounded; }}
.og img.photo {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 50% 40%; }}
.og::after {{ content: ""; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(6,6,6,.55) 0%, rgba(6,6,6,0) 30%, rgba(6,6,6,0) 45%, rgba(6,6,6,.7) 100%); }}
.logo {{ position: absolute; z-index: 1; left: 56px; top: 44px; width: 150px; }}
.caps {{ position: absolute; z-index: 1; left: 56px; bottom: 236px; font-size: 14px; letter-spacing: .62em;
  text-transform: uppercase; line-height: 1.4; }}
.giant {{ position: absolute; z-index: 1; left: 50px; bottom: 34px; margin: 0; font-weight: 700; font-size: 250px;
  line-height: .85; letter-spacing: -.03em; text-transform: uppercase; }}
</style></head><body><div class="og">
<img class="photo" src="{MASTER.as_uri()}" alt="">
<img class="logo" src="{(SITE / 'logo/logo-light.svg').as_uri()}" alt="">
<div class="caps">Частные</div>
<p class="giant">Балы</p>
</div></body></html>"""


def main():
    page_file = HERE / ".cache" / "og.html"
    page_file.write_text(HTML, encoding="utf-8")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": W, "height": H})
        page.goto(page_file.as_uri())
        page.wait_for_timeout(300)
        png = HERE / ".cache" / "og.png"
        page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": W, "height": H})
        b.close()
    im = Image.open(png).convert("RGB")
    im.save(SITE / "og.jpg", quality=85, optimize=True, progressive=True)
    (HERE.parent / "сверка" / "логотип").mkdir(parents=True, exist_ok=True)
    im.save(HERE.parent / "сверка" / "логотип" / "v1_og.png")
    print("site/og.jpg", (SITE / "og.jpg").stat().st_size // 1024, "КБ")


if __name__ == "__main__":
    main()
