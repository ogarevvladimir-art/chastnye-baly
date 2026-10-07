"""Apply the Terra tone polynomial to the two photos of block 04 B+D and write previews."""
import os
import numpy as np
from PIL import Image

SP = os.path.dirname(os.path.abspath(__file__))
PH = r"C:\Users\ogare\Desktop\Мои документы\Plyaskin group\Частные балы сайт\assets\photos"
Wt = np.load(os.path.join(SP, "W_terra_deg3.npy"))


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
    h, w, _ = a.shape
    out = np.empty_like(a)
    flat = a.reshape(-1, 3)
    res = out.reshape(-1, 3)
    step = 400000
    for i in range(0, len(flat), step):
        res[i:i + step] = feats(flat[i:i + step]) @ Wt
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))


jobs = {
    # name: (file, crop box in source px or None, output size)
    "t04_zriteli": ("KOR_1385_1.jpg", None, (2400, 1600)),
    "t04_uchastniki": ("0533.jpg", (0, 2300, 3648, 2300 + 2432), (2400, 1600)),
}
for name, (fn, box, size) in jobs.items():
    im = Image.open(os.path.join(PH, fn)).convert("RGB")
    if box:
        im = im.crop(box)
    im = im.resize(size, Image.LANCZOS)
    t = tone(im)
    t.save(os.path.join(SP, name + ".jpg"), quality=88)
    print(name, t.size, os.path.getsize(os.path.join(SP, name + ".jpg")) // 1024, "KB")

# previews: portrait object crop (416x560) of zriteli, landscape 1440x960 of uchastniki
z = Image.open(os.path.join(SP, "t04_zriteli.jpg"))
r = 560 / 416
cw = int(z.height / r)
x0 = (z.width - cw) // 2
zp = z.crop((x0, 0, x0 + cw, z.height)).resize((416, 560))
u = Image.open(os.path.join(SP, "t04_uchastniki.jpg")).resize((720, 480))
sheet = Image.new("RGB", (416 + 720 + 20, 560), (0x65, 0x36, 0x24))
sheet.paste(zp, (0, 0))
sheet.paste(u, (436, 0))
sheet.save(os.path.join(SP, "t04_preview.jpg"), quality=85)
