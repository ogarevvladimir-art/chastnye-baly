"""Section 06 (Slate, b/w stack): fit deg-3 RGB->RGB from Figma render vs source, apply to the new photo."""
import os
import numpy as np
from PIL import Image
from itertools import combinations_with_replacement as cwr

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = r"c:\Users\ogare\Desktop\Мои документы\VS CODE\.figma-mcp-cache"
SP = r"C:\Users\ogare\AppData\Local\Temp\claude\c--Users-ogare-Desktop---------------VS-CODE\f4567758-869f-4f3d-a59b-d595f179b619\scratchpad"
PH = r"C:\Users\ogare\Desktop\Мои документы\Plyaskin group\Частные балы сайт\assets\photos"


def feats(x, deg=3):
    cols = [np.ones(len(x))]
    for d in range(1, deg + 1):
        for c in cwr(range(3), d):
            cols.append(np.prod(x[:, list(c)], axis=1))
    return np.stack(cols, 1)


def load(src, rend):
    b = Image.open(rend).convert("RGB")
    a = Image.open(src).convert("RGB").resize(b.size, Image.LANCZOS)
    return (np.asarray(a, np.float64) / 255).reshape(-1, 3), (np.asarray(b, np.float64) / 255).reshape(-1, 3)


def tone(im, W):
    n = np.asarray(im.convert("RGB"), np.float64) / 255
    out = np.clip(feats(n.reshape(-1, 3)) @ W, 0, 1).reshape(n.shape)
    return Image.fromarray((out * 255).round().astype(np.uint8))


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    A = load(os.path.join(PH, "nk-08.jpg"), os.path.join(CACHE, "r6a.png"))
    B = load(os.path.join(SP, "src6b.jpg"), os.path.join(CACHE, "r6b.png"))

    def samp(d, n=300000):
        i = rng.choice(len(d[0]), min(n, len(d[0])), replace=False)
        return d[0][i], d[1][i]

    As, Bs = samp(A), samp(B)
    fit = lambda x, y: np.linalg.lstsq(feats(x), y, rcond=None)[0]
    mae = lambda W, x, y: np.abs(feats(x) @ W - y).mean() * 255
    Wa, Wb = fit(*As), fit(*Bs)
    W = fit(np.vstack([As[0], Bs[0]]), np.vstack([As[1], Bs[1]]))
    print("A->B", round(mae(Wa, *Bs), 2), "B->A", round(mae(Wb, *As), 2),
          "all A", round(mae(W, *As), 2), "all B", round(mae(W, *Bs), 2))
    np.save(os.path.join(HERE, "W06_slate_deg3.npy"), W)
    src = Image.open(os.path.join(PH, "@buzin_photo-1167.jpg")).convert("RGB").resize((1200, 1500), Image.LANCZOS)
    tone(src, W).save(os.path.join(HERE, "t06_03_bez_pary_buzin1167.jpg"), quality=88)
    print("ok")
