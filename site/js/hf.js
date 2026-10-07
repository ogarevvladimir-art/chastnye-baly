// Hero → Форматы, десктоп (≥ 1024). Заметка 223:2260.
//  · data-docked на .hf — слово БАЛЫ дошло до шва (низ sticky-слова упёрся в низ дорожки): только тогда наведение
//    опускает его на y 313 Форматов.
//  · data-seam на .hf — пройдена половина пути слова к шву: «ЧАСТНЫЕ» и «↓» гаснут (переход 0,3 с, не скраб).
//  · data-state на Форматах: rest / private / corporate. Мышь — наведение на половину; клавиатура — фокус внутри половины;
//    касание на широком экране — тап по половине.
//  · --drop на .hf (Д2, «в экран») — верх «БАЛЫ» в наведении от верха Форматов: 313s, но буквы не выше, чем на 24 под самым
//    высоким описанием (одна высота для обоих наведений). Если название в наведении попадает под колонку описания (1024),
//    оно встаёт на 24 под описание, слово — на 73s ниже названия. --lw-p / --lw-c — ширины «Обсудить … →»: колонка не уже ссылки.

const DOCK_TRAVEL = 1.0436; // путь слова до шва, em гиганта: (528 → 887) / 344
const CAP = 0.05; // от верха строки «БАЛЫ» (lh 0,85) до верха букв, em

export function initHF() {
  const hf = document.querySelector(".hf");
  if (!hf) return;
  const formats = hf.querySelector(".s-formats");
  const track = hf.querySelector(".hf__track");
  const word = hf.querySelector(".hf__word");
  const halves = [...formats.querySelectorAll(".fmt")];
  const desk = matchMedia("(min-width: 1024px)");
  const fine = matchMedia("(hover: hover) and (pointer: fine)");

  const flag = (name, on) => (on ? (hf.dataset[name] = "") : delete hf.dataset[name]);

  let raf = 0;
  const check = () => {
    raf = 0;
    if (!desk.matches) {
      flag("docked", false);
      flag("seam", false);
      return;
    }
    const remain = track.getBoundingClientRect().bottom - word.getBoundingClientRect().bottom;
    const fs = parseFloat(getComputedStyle(track).fontSize);
    flag("docked", remain < 1);
    flag("seam", remain < (DOCK_TRAVEL * fs) / 2);
  };
  const schedule = () => raf || (raf = requestAnimationFrame(check));
  addEventListener("scroll", schedule, { passive: true });
  addEventListener("resize", schedule);
  check();

  const [priv, corp] = halves;
  const part = (half, sel) => half.querySelector(sel);
  const place = () => {
    for (const name of ["--drop", "--lw-p", "--lw-c"]) hf.style.removeProperty(name);
    if (!desk.matches) return;
    hf.style.setProperty("--lw-p", part(priv, ".fmt__link").offsetWidth + "px");
    hf.style.setProperty("--lw-c", part(corp, ".fmt__link").offsetWidth + "px");
    const u = (Math.min(document.documentElement.clientWidth, 1920) - 128) / 1312;
    const s = Math.min(u, formats.offsetHeight / 900);
    const descs = [part(priv, ".fmt__desc"), part(corp, ".fmt__desc")];
    const low = Math.max(...descs.map((d) => d.offsetTop + d.offsetHeight));
    const fs = parseFloat(getComputedStyle(track).fontSize);
    // Название в наведении (x «корпоративных» сдвигается на −360u) заходит под колонку описания с зазором меньше 24?
    const under = (title, dx, desc) =>
      title.offsetLeft + dx < desc.offsetLeft + desc.offsetWidth + 24 &&
      title.offsetLeft + dx + title.offsetWidth + 24 > desc.offsetLeft;
    let drop = Math.max(313 * s, low + 24 - CAP * fs);
    if (under(part(priv, ".fmt__title"), 0, descs[0]) || under(part(corp, ".fmt__title"), -360 * u, descs[1])) {
      drop = Math.max(drop, low + 24 + 73 * s);
    }
    hf.style.setProperty("--drop", drop.toFixed(1) + "px");
  };
  new ResizeObserver(place).observe(formats);
  document.fonts.ready.then(place);

  const set = (state) => {
    if (!desk.matches) state = "rest";
    formats.dataset.state = state;
    state === "rest" ? delete hf.dataset.formats : (hf.dataset.formats = state);
  };

  for (const half of halves) {
    half.addEventListener("pointerenter", (e) => {
      if (e.pointerType === "mouse") set(half.dataset.half);
    });
    half.addEventListener("focusin", () => set(half.dataset.half));
    half.addEventListener("click", (e) => {
      if (fine.matches || !desk.matches || e.target.closest("a")) return;
      set(formats.dataset.state === half.dataset.half ? "rest" : half.dataset.half);
    });
  }
  formats.addEventListener("pointerleave", (e) => {
    if (e.pointerType === "mouse" && !formats.contains(document.activeElement)) set("rest");
  });
  formats.addEventListener("focusout", (e) => {
    if (!formats.contains(e.relatedTarget) && !formats.matches(":hover")) set("rest");
  });
  desk.addEventListener("change", () => set("rest"));
}
