"""Block 05 «Два полюса»: check the Ash polynomial W5_deg3 against a Figma render,
then bake it into three 928x560 (@2x) scene photos."""
import os
import sys
import numpy as np
from PIL import Image, ImageFilter

SP = os.path.dirname(os.path.abspath(__file__))
DOCS = r"C:\Users\ogare\Desktop\Мои документы"
PH = os.path.join(DOCS, r"Plyaskin group\Частные балы сайт\assets\photos")
# fitted by fit05.py on renders of ball-07 and KOR_0404_1 (err 0.4/255, cross-check <= 1.1/255)
Wt = np.load(os.path.join(SP, "W05_ash_deg3.npy"))


def feats(X, deg=3):
    r, g, bb = X[:, 0], X[:, 1], X[:, 2]
    cols = [np.ones(len(X))]
    for i in range(deg + 1):
        for j in range(deg + 1 - i):
            for k in range(deg + 1 - i - j):
                if i + j + k:
                    cols.append(r ** i * g ** j * bb ** k)
    return np.stack(cols, 1)


def tone(im):
    a = np.asarray(im.convert("RGB"), dtype=np.float64) / 255
    flat = a.reshape(-1, 3)
    out = np.empty_like(flat)
    for i in range(0, len(flat), 400000):
        out[i:i + 400000] = feats(flat[i:i + 400000]) @ Wt
    return Image.fromarray((np.clip(out.reshape(a.shape), 0, 1) * 255 + 0.5).astype(np.uint8))


def fill(im, W, H, box=None):
    if box:
        im = im.crop(box)
    s = max(W / im.width, H / im.height)
    ox, oy = (im.width * s - W) / 2, (im.height * s - H) / 2
    return im.resize((W, H), Image.LANCZOS, box=(ox / s, oy / s, (ox + W) / s, (oy + H) / s))


# bake
OUT = os.path.join(DOCS, r"Plyaskin group\Частные балы сайт\Доработка\фото-тон\05-шоу")
os.makedirs(OUT, exist_ok=True)
jobs = {
    "t05_professionaly": ("nk-05.jpg", None),
    "t05_sovmestny": ("nk-01.jpg", None),
    # KOR_0404_1 dropped: the sponsor logo stays in any crop that keeps the heads
    "t05_nomer_ot_svoih": ("NesterovaMaria_0041_resized.jpg", None),
}
prev = []
for name, (fn, box) in jobs.items():
    im = fill(Image.open(os.path.join(PH, fn)).convert("RGB"), 1856, 1120, box)
    t = tone(im)
    t.save(os.path.join(OUT, name + ".jpg"), quality=88)
    prev.append(t.resize((464, 280)))
    print(name, t.size, os.path.getsize(os.path.join(OUT, name + ".jpg")) // 1024, "KB")
sheet = Image.new("RGB", (464 * 3 + 16, 280), (0x3E, 0x3E, 0x3E))
for i, p in enumerate(prev):
    sheet.paste(p, (i * 472, 0))
sheet.save(os.path.join(SP, "t05_preview.jpg"), quality=85)
