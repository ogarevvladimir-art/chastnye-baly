// Анимации входа (ПЕРЕДАЧА 3). Триггер — верх элемента на 90 % высоты экрана, один раз, доигрывает сама (не скраб).
// Анимируются только transform и opacity. При prefers-reduced-motion и html.no-motion — кадр покоя без анимации.
// window.__motion — входы запущены (страховка в index.html).
//
//   data-giant            — гигант собирается из букв: буква n стартует с translateX((n+1)em) scaleX(3), opacity 0,
//                           задержка 0,15 + 0,05n с, буква 0,8 с, expo-out. Вертикальный гигант (writing-mode: vertical-rl
//                           + rotate(180deg), этап 3) — то же вдоль строки: translateY / scaleY, сдвиг идёт по ходу чтения.
//   data-reveal="text"    — проявление: opacity 0 → 1, translateY(16px) → 0, 0,8 с.
//   data-reveal="fade"    — только opacity, 0,8 с ease-out.
//   data-reveal="bar"     — отрезок партитуры: scaleX 0 → 1 от левого края, 0,8 с.
//   data-photo            — фото: scale(1.1) → 1 внутри рамки с overflow: hidden, 1,2 с expo-out.
//   data-delay="0.3"      — задержка старта, с.
//   data-rise="24"        — подъём текста при проявлении, px (по умолчанию 16; панель 08 — 24).
// Элемент, у которого data-in уже стоит до старта (слова неактивных форматов 05), входа не получает.

const EXPO = "cubic-bezier(0.16, 1, 0.3, 1)";
const TEXT = "cubic-bezier(0.33, 1, 0.68, 1)";
const SEL = "[data-giant], [data-reveal], [data-photo]";

export const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");

const isVertical = (el) => getComputedStyle(el).writingMode.startsWith("vertical");

// Буквы — inline-block, иначе их не растянуть. Кернинг между отдельными span теряется,
// поэтому позиции букв в целом слове замеряются заранее и разница возвращается отступом в начале строки
// (margin-inline-start, в em) — он работает и в горизонтальном, и в вертикальном слове.
function splitGiant(el) {
  if (el.querySelector(".g-l")) return;
  const text = el.textContent;
  const node = el.firstChild;
  const range = document.createRange();
  const rects = [];
  for (let i = 0; i < text.length; i++) {
    range.setStart(node, i);
    range.setEnd(node, i + 1);
    rects.push(range.getBoundingClientRect());
  }
  // Координата вдоль хода чтения: в горизонтальном слове — left; в вертикальном (повёрнутом на 180°) слово
  // читается снизу вверх, поэтому — минус bottom
  const vertical = isVertical(el);
  const up = vertical && rects.length > 1 && rects[0].top > rects[rects.length - 1].top;
  const pos = (r) => (!vertical ? r.left : up ? -r.bottom : r.top);
  const before = rects.map(pos);
  el.textContent = "";
  const letters = [];
  for (const ch of text) {
    if (ch === " ") {
      el.append(" ");
      letters.push(null);
      continue;
    }
    const s = document.createElement("span");
    s.className = "g-l";
    s.textContent = ch;
    el.append(s);
    letters.push(s);
  }
  const fs = parseFloat(getComputedStyle(el).fontSize);
  const after = letters.map((s) => (s ? pos(s.getBoundingClientRect()) : null));
  // Отсчёт — от первой буквы: в вертикальной строке inline-block стоит со своим постоянным сдвигом, переносить его на слово не нужно
  let prev = before[0] - after[0];
  letters.forEach((s, i) => {
    if (!s) return;
    const d = before[i] - after[i];
    if (Math.abs(d - prev) > 0.05) s.style.marginInlineStart = ((d - prev) / fs).toFixed(4) + "em";
    prev = d;
  });
}

function run(target, keyframes, options) {
  target.style.willChange = "transform, opacity";
  const a = target.animate(keyframes, { fill: "backwards", ...options });
  a.finished.then(() => (target.style.willChange = ""), () => {});
  return a;
}

function play(el) {
  const delay = parseFloat(el.dataset.delay || 0) * 1000;
  el.dataset.in = "";

  if (el.hasAttribute("data-giant")) {
    const v = isVertical(el);
    el.querySelectorAll(".g-l").forEach((l, n) => {
      l.style.transformOrigin = v ? "50% 0" : "";
      run(l, [
        { transform: v ? `translateY(${n + 1}em) scaleY(3)` : `translateX(${n + 1}em) scaleX(3)`, opacity: 0 },
        { transform: "none", opacity: 1 },
      ], { duration: 800, delay: delay + 150 + 50 * n, easing: EXPO });
    });
    return;
  }

  if (el.dataset.reveal === "bar") {
    run(el, [{ transform: "scaleX(0)" }, { transform: "none" }], { duration: 800, delay, easing: TEXT });
    return;
  }

  if (el.hasAttribute("data-photo")) {
    const img = el.querySelector("img");
    if (img) run(img, [{ transform: "scale(1.1)" }, { transform: "none" }], { duration: 1200, delay, easing: EXPO });
    return;
  }

  if (el.dataset.reveal === "fade") {
    run(el, [{ opacity: 0 }, { opacity: 1 }], { duration: 800, delay, easing: "ease-out" });
    return;
  }

  run(el, [
    { opacity: 0, transform: `translateY(${el.dataset.rise || 16}px)` },
    { opacity: 1, transform: "none" },
  ], { duration: 800, delay, easing: TEXT });
}

// Шрифты гигантов (Unbounded Bold): буквы режутся по замеру, поэтому ждём только их, а не все шрифты страницы (LCP — «БАЛЫ»)
const fontsOf = (els) => Promise.all([...new Set(els.map((el) => {
  const s = getComputedStyle(el);
  return `${s.fontStyle} ${s.fontWeight} 1em ${s.fontFamily}`;
}))].map((f) => document.fonts.load(f)));

const off = () => document.documentElement.classList.contains("no-motion");

export async function initMotion(root = document) {
  const els = [...root.querySelectorAll(SEL)].filter((el) => !("in" in el.dataset));
  const still = () => els.forEach((el) => (el.dataset.in = ""));
  if (off() || reducedMotion.matches || !("IntersectionObserver" in window) || !Element.prototype.animate) return still();

  const giants = els.filter((el) => el.hasAttribute("data-giant"));
  await fontsOf(giants);
  // Страховка (index.html) уже включила no-motion — страница видна целиком, входы не запускаем
  if (off()) return still();
  giants.forEach(splitGiant);

  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      io.unobserve(e.target);
      play(e.target);
    }
  }, { rootMargin: "0px 0px -10% 0px" });

  els.forEach((el) => io.observe(el));
  window.__motion = true;
}
