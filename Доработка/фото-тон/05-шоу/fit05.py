"""Fit the Ash «фото с цветом» tone of block 05 on two renders (ball-07, KOR_0404_1),
cross-check each on the other, compare with the old W5_deg3, save W05_ash_deg3.npy."""
import os
import numpy as np
from PIL import Image, ImageFilter

SP = os.path.dirname(os.path.abspath(__file__))
DOCS = r"C:\Users\ogare\Desktop\Мои документы"
PH = os.path.join(DOCS, r"Plyaskin group\Частные балы сайт\assets\photos")
SH = os.path.join(DOCS, r"VS CODE\.figma-shots")


def feats(X, deg=3):
    r, g, bb = X[:, 0], X[:, 1], X[:, 2]
    cols = [np.ones(len(X))]
    for i in range(deg + 1):
        for j in range(deg + 1 - i):
            for k in range(deg + 1 - i - j):
                if i + j + k:
                    cols.append(r ** i * g ** j * bb ** k)
    return np.stack(cols, 1)


def pair(src_name, ref_name, node_size, window):
    # the export is clipped by the parent «Кадр» (456x560): FILL into the node, then cut the visible window
    ref = Image.open(os.path.join(SH, ref_name)).convert("RGB")
    src = Image.open(os.path.join(PH, src_name)).convert("RGB")
    W, H = node_size
    s = max(W / src.width, H / src.height)
    ox, oy = (src.width * s - W) / 2, (src.height * s - H) / 2
    crop = src.resize((W, H), Image.LANCZOS, box=(ox / s, oy / s, (ox + W) / s, (oy + H) / s)).crop(window)
    assert crop.size == ref.size, (crop.size, ref.size)
    a = np.asarray(crop.filter(ImageFilter.GaussianBlur(2)), dtype=np.float64).reshape(-1, 3) / 255
    b = np.asarray(ref.filter(ImageFilter.GaussianBlur(2)), dtype=np.float64).reshape(-1, 3) / 255
    return a, b


P = {"ball-07": pair("ball-07.jpg", "t05_ref_s01_vis.png", (520, 780), (16, 170, 472, 730)),
     "KOR_0404": pair("KOR_0404_1.jpg", "t05_ref_s02_vis.png", (840, 560), (200, 0, 656, 560))}


def err(W, X, Y):
    e = np.abs(feats(X) @ W - Y) * 255
    return e.mean(), np.percentile(e, 95)


for k, (X, Y) in P.items():
    print(k, "identity err %.2f" % (np.abs(X - Y).mean() * 255))
old = np.load(os.path.join(DOCS, r"VS CODE\.figma-mcp-cache\W5_deg3.npy"))
for k, (X, Y) in P.items():
    print(k, "old W5 err %.2f p95 %.2f" % err(old, X, Y))
rng = np.random.default_rng(0)
Ws = {}
for k, (X, Y) in P.items():
    idx = rng.choice(len(X), min(150000, len(X)), replace=False)
    Ws[k] = np.linalg.lstsq(feats(X[idx]), Y[idx], rcond=None)[0]
for k, W in Ws.items():
    for k2, (X, Y) in P.items():
        print("fit on", k, "-> test", k2, "err %.2f p95 %.2f" % err(W, X, Y))
X = np.concatenate([P[k][0] for k in P])
Y = np.concatenate([P[k][1] for k in P])
idx = rng.choice(len(X), 250000, replace=False)
Wb = np.linalg.lstsq(feats(X[idx]), Y[idx], rcond=None)[0]
for k, (X1, Y1) in P.items():
    print("both ->", k, "err %.2f p95 %.2f" % err(Wb, X1, Y1))
np.save(os.path.join(SP, "W05_ash_deg3.npy"), Wb)
