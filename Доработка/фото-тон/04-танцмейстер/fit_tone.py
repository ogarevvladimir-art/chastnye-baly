"""Fit a degree-3 RGB->RGB polynomial that reproduces the Terra "photo with colour" tone
from a Figma render of 191:689 (NesterovaMaria_0126 with the fill stack)."""
import os
import numpy as np
from PIL import Image, ImageFilter

SP = os.path.dirname(os.path.abspath(__file__))
DOCS = r"C:\Users\ogare\Desktop\Мои документы"
src = Image.open(os.path.join(DOCS, r"Plyaskin group\Частные балы сайт\assets\photos\NesterovaMaria_0126_resized.jpg")).convert("RGB")
ref = Image.open(os.path.join(DOCS, r"VS CODE\.figma-shots\t04_tone_ref.png")).convert("RGB")
print("src", src.size, "ref", ref.size)

W, H = ref.size
sw, sh = src.size
s = max(W / sw, H / sh)
ox, oy = (sw * s - W) / 2, (sh * s - H) / 2
box = (ox / s, oy / s, (ox + W) / s, (oy + H) / s)
crop = src.resize((W, H), Image.BICUBIC, box=box)

a = np.asarray(crop.filter(ImageFilter.GaussianBlur(2)), dtype=np.float64) / 255
b = np.asarray(ref.filter(ImageFilter.GaussianBlur(2)), dtype=np.float64) / 255
X, Y = a.reshape(-1, 3), b.reshape(-1, 3)


def feats(X, deg=3):
    r, g, bb = X[:, 0], X[:, 1], X[:, 2]
    cols = [np.ones(len(X))]
    for i in range(deg + 1):
        for j in range(deg + 1 - i):
            for k in range(deg + 1 - i - j):
                if i + j + k:
                    cols.append(r ** i * g ** j * bb ** k)
    return np.stack(cols, 1)


idx = np.random.default_rng(0).choice(len(X), min(200000, len(X)), replace=False)
Wt = np.linalg.lstsq(feats(X[idx]), Y[idx], rcond=None)[0]
err = np.abs(feats(X) @ Wt - Y) * 255
print("mean err %.2f  p95 %.2f  max %.1f" % (err.mean(), np.percentile(err, 95), err.max()))
print("ref mean", (Y.mean(0) * 255).round(1), "src mean", (X.mean(0) * 255).round(1))
np.save(os.path.join(SP, "W_terra_deg3.npy"), Wt)
