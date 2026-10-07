"""Склейка «Figma | сайт» в одну картинку для показа пользователю.

  python tools/pair.py figma.png site.png -o сверка/01/pair_390.png
  python tools/pair.py figma.png site.png -o out.png --diff     # третья панель: разница (светлое — расхождение)

Обе картинки приводятся к одной ширине (по Figma). Если Figma снята с scale 2, а сайт с dpr 1 — масштаб выравнивается сам.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

BG = (40, 40, 40)
LABEL = (255, 200, 0)


def font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("figma")
    ap.add_argument("site")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--diff", action="store_true")
    ap.add_argument("--labels", nargs=2, default=["Figma", "Сайт"])
    ap.add_argument("--max-height", type=int, default=0, help="обрезать по высоте (0 — без обрезки)")
    args = ap.parse_args()

    a = Image.open(args.figma).convert("RGB")
    b = Image.open(args.site).convert("RGB")
    if b.width != a.width:
        b = b.resize((a.width, round(b.height * a.width / b.width)), Image.LANCZOS)
    h = max(a.height, b.height)
    if args.max_height:
        h = min(h, args.max_height)
    panels = [a, b]
    labels = list(args.labels)
    if args.diff:
        aa = Image.new("RGB", (a.width, h), BG)
        aa.paste(a)
        bb = Image.new("RGB", (a.width, h), BG)
        bb.paste(b)
        panels.append(ImageOps.autocontrast(ImageChops.difference(aa, bb)))
        labels.append("Разница")

    gap, top = 16, 36
    W = sum(p.width for p in panels) + gap * (len(panels) + 1)
    out = Image.new("RGB", (W, h + top + gap), BG)
    d = ImageDraw.Draw(out)
    f = font(20)
    x = gap
    for p, lab in zip(panels, labels):
        d.text((x, 8), f"{lab}  {p.width}×{p.height}", fill=LABEL, font=f)
        out.paste(p.crop((0, 0, p.width, min(p.height, h))), (x, top))
        x += p.width + gap
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.save(args.out)
    print(args.out, out.size)


if __name__ == "__main__":
    main()
