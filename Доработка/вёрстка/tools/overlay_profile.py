"""Профиль затемнения кадра: рендер Figma (с градиентом) против тонированного файла site/img (без градиента).
a = (фото − рендер) / (фото − Ink) по строкам и столбцам, медиана по пикселям с достаточным сигналом.
Запуск: python overlay_profile.py <рендер.png> <фото.jpg> [x y w h — окно фото в кадре рендера, px макета]"""
import sys
import numpy as np
from PIL import Image

render_p, photo_p = sys.argv[1], sys.argv[2]
r = Image.open(render_p).convert("RGB")
p = Image.open(photo_p).convert("RGB")
if len(sys.argv) > 3:
    x, y, w, h = map(int, sys.argv[3:7])
    s = r.width / int(sys.argv[7]) if len(sys.argv) > 7 else 2
    r = r.crop((int(x * s), int(y * s), int((x + w) * s), int((y + h) * s)))
r = np.asarray(r.resize(p.size, Image.LANCZOS), dtype=float).mean(axis=2)
p = np.asarray(p, dtype=float).mean(axis=2)
ink = 6.0
d = p - ink
a = np.where(d > 25, (p - r) / np.maximum(d, 1), np.nan)
H, W = a.shape
print("rows (y%  alpha):")
for i in range(0, 21):
    y0 = int(i / 20 * (H - 1))
    band = a[max(0, y0 - 2): y0 + 3]
    print(f"  {i*5:3d}%  {np.nanmedian(band):.3f}")
print("cols (x%  alpha):")
for i in range(0, 11):
    x0 = int(i / 10 * (W - 1))
    band = a[:, max(0, x0 - 2): x0 + 3]
    print(f"  {i*10:3d}%  {np.nanmedian(band):.3f}")
