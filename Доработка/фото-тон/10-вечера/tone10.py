"""10 «Вечера»: фото со старого сайта ballevent.ru в тон Ink (W10_ink_deg3). Правые 4% срезаны — подпись фотографа."""
import os
import numpy as np
from PIL import Image
from fit10 import feats

HERE = os.path.dirname(os.path.abspath(__file__))
BE = r"C:\Users\ogare\Desktop\Мои документы\Plyaskin group\Частные балы сайт\assets\photos\ballevent"
Wt = np.load(os.path.join(HERE, "W10_ink_deg3.npy"))


def tone(im):
    a = np.asarray(im, np.float64) / 255
    out = feats(a.reshape(-1, 3)) @ Wt
    return Image.fromarray((np.clip(out.reshape(a.shape), 0, 1) * 255 + 0.5).astype(np.uint8))


jobs = {  # name: (file, crop box)
    "t10_omega_obj": ("omega/omega_14.jpg", (240, 0, 880, 800)),
    "t10_kash_obj": ("kashemir/kashemir_17.jpg", (280, 0, 920, 800)),
    "t10_omega_wide": ("omega/omega_14.jpg", (0, 0, 1152, 768)),
    "t10_omega_wide2": ("omega/omega_11.jpg", (0, 0, 1152, 768)),
    "t10_kash_wide": ("kashemir/kashemir_17.jpg", (0, 16, 1152, 784)),
    "t10_kash_wide2": ("kashemir/kashemir_14.jpg", (0, 0, 1152, 768)),
}
for name, (fn, box) in jobs.items():
    im = Image.open(os.path.join(BE, fn)).convert("RGB").crop(box)
    tone(im).save(os.path.join(HERE, name + ".jpg"), quality=90)
    print(name, im.size)

# 2026-09-29: вариант B — по 4 фото на вечер, вертикали 4:5 (640×800)
jobs2 = {
    "t10_omega_a": ("omega/omega_11.jpg", (340, 0, 980, 800)),
    "t10_omega_c": ("omega/omega_16.jpg", (510, 0, 1150, 800)),
    "t10_omega_d": ("omega/omega_10.jpg", (280, 0, 920, 800)),
    "t10_kash_a": ("kashemir/kashemir_16.jpg", (136, 0, 776, 800)),
    "t10_kash_c": ("kashemir/kashemir_14.jpg", (280, 0, 920, 800)),
    "t10_kash_d": ("kashemir/kashemir_10.jpg", (280, 0, 920, 800)),
}
if __name__ == "__main__":
    for name, (fn, box) in jobs2.items():
        im = Image.open(os.path.join(BE, fn)).convert("RGB").crop(box)
        tone(im).save(os.path.join(HERE, name + ".jpg"), quality=90)
        print(name, im.size)
