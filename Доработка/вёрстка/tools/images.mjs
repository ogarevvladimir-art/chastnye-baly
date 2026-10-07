// Фото сайта: мастер (кроп + тон, готовит build_photos.py) → AVIF / WebP / JPEG по ширинам в site/img/<блок>/.
//
//   python build_photos.py          # сначала мастера и манифест images.json
//   node images.mjs                 # все записи манифеста
//   node images.mjs hero            # только блок hero
//   node images.mjs --dry           # показать, что будет сделано, без записи
//
// Запись манифеста:
//   { "block": "hero", "name": "arch", "media": "m", "src": "Доработка/вёрстка/tools/.cache/masters/hero-arch-m.png",
//     "frame": [390, 780], "widths": [390, 540] }
// Выход: site/img/hero/arch-m-390.avif, …-m-540.avif и т. д. Апскейла нет: ширины уже ограничены исходником.

import { readFile, mkdir, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const TOOLS = path.dirname(fileURLToPath(import.meta.url));
const PROJECT = path.resolve(TOOLS, "../../..");
const OUT = path.join(PROJECT, "site", "img");

// Качество — под ≤ 200 КБ AVIF на телефоне (самый крупный файл телефона — 3×)
const FORMATS = {
  avif: { quality: 50, effort: 6, chromaSubsampling: "4:2:0" },
  webp: { quality: 72, effort: 5 },
  jpg: { quality: 78, mozjpeg: true, progressive: true },
};

const args = process.argv.slice(2);
const dry = args.includes("--dry");
const only = args.filter((a) => !a.startsWith("--"));

const manifest = JSON.parse(await readFile(path.join(TOOLS, "images.json"), "utf8"));
const report = [];
let total = 0;

for (const item of manifest.images) {
  if (only.length && !only.includes(item.block)) continue;
  const src = path.join(PROJECT, item.src);
  const [fw, fh] = item.frame;
  const dir = path.join(OUT, item.block);
  if (!dry) await mkdir(dir, { recursive: true });
  for (const w of item.widths) {
    const h = Math.round((w * fh) / fw);
    const base = `${item.name}-${item.media}-${w}`;
    if (dry) {
      report.push(`${item.block}/${base}.{avif,webp,jpg}  ${w}×${h}`);
      continue;
    }
    const pipeline = sharp(src).resize(w, h, { fit: "fill", kernel: "lanczos3" });
    const sizes = [];
    for (const [ext, opts] of Object.entries(FORMATS)) {
      const file = path.join(dir, `${base}.${ext}`);
      const info = await pipeline.clone().toFormat(ext === "jpg" ? "jpeg" : ext, opts).toFile(file);
      sizes.push(`${ext} ${(info.size / 1024).toFixed(0)}`);
      total += info.size;
    }
    report.push(`${item.block}/${base}  ${w}×${h}  ${sizes.join(" / ")} КБ`);
  }
}

console.log(report.join("\n") || "Манифест пуст.");
if (!dry) console.log(`\nвсего ${(total / 1024 / 1024).toFixed(1)} МБ`);
