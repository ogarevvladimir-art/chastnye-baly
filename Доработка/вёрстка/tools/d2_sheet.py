"""Лист кадров Д2 из Figma: строки — окна, столбцы — hero / покой / наведения.
  python tools/d2_sheet.py <префикс файлов в .figma-shots> <выход.png>"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SHOTS = Path(r"C:\Users\ogare\Desktop\Мои документы\VS CODE\.figma-shots")
WINDOWS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
COLS = ["hero", "rest", "private", "corporate"]


def main(prefix, out, col_w=560):
    font = ImageFont.truetype("arial.ttf", 22)
    rows = []
    for w, h in WINDOWS:
        ims = []
        for c in COLS:
            f = SHOTS / f"{prefix}_{w}_{c}.png"
            if f.exists():
                im = Image.open(f).convert("RGB")
                ims.append(im.resize((col_w, round(im.height * col_w / im.width))))
        if ims:
            rows.append((f"{w}×{h}", ims))
    pad, head = 16, 34
    W = pad + len(COLS) * (col_w + pad)
    H = sum(head + max(i.height for i in ims) + pad for _, ims in rows) + pad
    sheet = Image.new("RGB", (W, H), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    y = pad
    for label, ims in rows:
        d.text((pad, y), label, fill=(220, 215, 205), font=font)
        y += head
        for i, im in enumerate(ims):
            sheet.paste(im, (pad + i * (col_w + pad), y))
        y += max(i.height for i in ims) + pad
    sheet.save(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
