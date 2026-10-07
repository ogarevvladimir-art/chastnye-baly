"""05 «Занавес», замена 2026-09-29: слайд 1 — ball-07 (как 191:705), слайд 2 — BI4A1223. Тон Ash (W05_ash_deg3)."""
import os
from PIL import Image
from tone05_zanaves_lib import tone, fill, PH, HERE

jobs = {  # name: (file, vertical focus 0 top .. 1 bottom)
    "t05z_01_ball07": ("ball-07.jpg", 0.58),
    "t05z_02_BI4A1223": ("BI4A1223.jpg", 0.2),
}
for name, (fn, fy) in jobs.items():
    im = fill(Image.open(os.path.join(PH, fn)).convert("RGB"), 2400, 1500, fy)
    tone(im).save(os.path.join(HERE, name + ".jpg"), quality=88)
    print(name, os.path.getsize(os.path.join(HERE, name + ".jpg")) // 1024, "KB")
