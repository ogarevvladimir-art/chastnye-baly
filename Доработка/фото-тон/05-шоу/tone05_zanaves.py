"""05 «Занавес»: full-bleed 1440x900 scene photos (@~1.7x, 2400x1500) in the Ash tone (W05_ash_deg3)."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PH = r"C:\Users\ogare\Desktop\Мои документы\Plyaskin group\Частные балы сайт\assets\photos"
Wt = np.load(os.path.join(HERE, "W05_ash_deg3.npy"))


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
    a = np.asarray(im, dtype=np.float64) / 255
    flat = a.reshape(-1, 3)
    out = np.empty_like(flat)
    for i in range(0, len(flat), 400000):
        out[i:i + 400000] = feats(flat[i:i + 400000]) @ Wt
    return Image.fromarray((np.clip(out.reshape(a.shape), 0, 1) * 255 + 0.5).astype(np.uint8))


def fill(im, W, H, fy=0.5):
    s = max(W / im.width, H / im.height)
    ox, oy = (im.width * s - W) / 2, (im.height * s - H) * fy
    return im.resize((W, H), Image.LANCZOS, box=(ox / s, oy / s, (ox + W) / s, (oy + H) / s))


jobs = {  # name: (file, vertical focus 0 top .. 1 bottom)
    "t05z_01_professionaly": ("nk-05.jpg", 0.6),
    "t05z_02_sovmestny": ("nk-01.jpg", 0.5),
    "t05z_03_nomer_ot_svoih": ("NesterovaMaria_0041_resized.jpg", 0.6),
}
for name, (fn, fy) in jobs.items():
    im = fill(Image.open(os.path.join(PH, fn)).convert("RGB"), 2400, 1500, fy)
    tone(im).save(os.path.join(HERE, name + ".jpg"), quality=86)
    print(name, os.path.getsize(os.path.join(HERE, name + ".jpg")) // 1024, "KB")
