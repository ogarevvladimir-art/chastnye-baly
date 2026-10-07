// Точка входа. Модули без сборки (ES-модули).
// Каждый блок запускается отдельно: ошибка в одном не останавливает остальные. Если входы не запустились — no-motion
// (всё видно). Модули пришли позже страховки (режим «без JS» уже включён) — возвращаем js без анимаций входа.

import { initMotion } from "./motion.js";
import { initHeader } from "./header.js";
import { initMenu } from "./menu.js";
import { initHF } from "./hf.js";
import { initBlocks } from "./blocks.js";
import { initForm } from "./form.js";

const html = document.documentElement;
window.__ready = true;
if (!html.classList.contains("js")) html.classList.add("js", "no-motion");

const noMotion = (err) => {
  console.error(err);
  html.classList.add("no-motion");
};

for (const init of [initHeader, initMenu, initHF, initBlocks, initForm]) {
  try {
    init();
  } catch (err) {
    console.error(err);
  }
}

try {
  initMotion().catch(noMotion);
} catch (err) {
  noMotion(err);
}
