"""10 «Вечера»: полином deg3 RGB→RGB для стека «фото с цветом» на Ink.
Эталон — рендер 198:810 (окно 1440×560 из узла 1440×2160 FILL, y 440) и исходник NesterovaMaria_0093."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PH = r"C:\Users\ogare\Desktop\Мои документы\Plyaskin group\Частные балы сайт\assets\photos"
REF = r"C:\Users\ogare\Desktop\Мои документы\VS CODE\.figma-mcp-cache\ink_ref_810.png"


def feats(X, deg=3):
    r, g, bb = X[:, 0], X[:, 1], X[:, 2]
    cols = [np.ones(len(X))]
    for i in range(deg + 1):
        for j in range(deg + 1 - i):
            for k in range(deg + 1 - i - j):
                if i + j + k:
                    cols.append(r ** i * g ** j * bb ** k)
    return np.stack(cols, 1)


def fill(im, W, H):
    s = max(W / im.width, H / im.height)
    ox, oy = (im.width * s - W) / 2, (im.height * s - H) / 2
    return im.resize((W, H), Image.LANCZOS, box=(ox / s, oy / s, (ox + W) / s, (oy + H) / s))


if __name__ == "__main__":
    src = fill(Image.open(os.path.join(PH, "NesterovaMaria_0093_resized.jpg")).convert("RGB"), 1440, 2160).crop((0, 440, 1440, 1000))
    ref = Image.open(REF).convert("RGB")
    a = np.asarray(src, np.float64).reshape(-1, 3) / 255
    b = np.asarray(ref, np.float64).reshape(-1, 3) / 255
    idx = np.random.default_rng(0).choice(len(a), 200000, replace=False)
    tr, te = idx[:150000], idx[150000:]
    W = np.linalg.lstsq(feats(a[tr]), b[tr], rcond=None)[0]
    err = np.abs(feats(a[te]) @ W - b[te]).mean() * 255
    print("mean abs err /255:", round(err, 2))
    np.save(os.path.join(HERE, "W10_ink_deg3.npy"), W)
