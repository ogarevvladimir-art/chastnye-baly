// Поведение блоков 01–10 (этапы 3–5).
//  · 01 Подготовка (десктоп): наведение на строку раскрывает описание, уход курсора выше или ниже списка — покой (заметка 219:1904).
//  · 02 Вечер (десктоп): весь блок одним экраном, список этапов — раскрыта наведённая строка, покой — 01 (заметка 223:2463).
//  · 03 Музыка: десктоп — колонка-переключатель (наведение, клик, фокус), покоя нет; телефон и планшет — счётчик карусели.
//  · 04 Танцмейстер (десктоп): наведение раскрывает панель, уход курсора со сцены — покой.
//  · 05 Шоу: телефон и планшет — свайп по сцене и тап по пункту; десктоп — сцена закреплена, формат = шаг прокрутки
//    (заметка 213:937), пункт прокручивает к своему шагу. reduced-motion на десктопе — без закрепления, пункты переключают.
//  · 06 Ассистент (десктоп): наведение, клик или фокус на вопросе меняют фото и ответ; покоя нет.
//  · 07 Уроки (десктоп): блок в экран, k лесенки — по высоте текста ступеней (Д3б).
//  · 08 Этикет: переключатель и тап по панели меняют роль; повторный тап во время смены (0,5 с) не принимается.
//  · 09 Дресс-код (этап 5): наведение на правило на десктопе; правила планшета и десктопа не наезжают друг на друга.
//  · 10 Вечера (этап 5): занавес, барабан и смена текста (как 05); свайп и тап, на десктопе — автосмена 4 с.
//  · 09, 10, Контакты (десктоп, Д3в): шаги k экранов тела и панели формы — по высоте окна.

import { hoverStates } from "./states.js";
import { reducedMotion } from "./motion.js";
import { createSwitch, setPositions, tabs, swipe, scrollSteps } from "./switch.js";

const desk = matchMedia("(min-width: 1024px)");

function initPrep() {
  const s = document.querySelector(".s-prep");
  if (!s) return;
  const steps = [...s.querySelectorAll(".prep__step")];
  steps.forEach((p, i) => (p.dataset.key = String(i + 1)));
  hoverStates(s, steps);
}

// 02 (Ц3): пять этапов — слои закреплённой сцены, шаг по прокрутке (scrollSteps, как 05); плёнка фото и барабан слова — CSS по data-pos.
// Закрепление (data-pin) — с JS и без reduced-motion. Телефон и планшет: высота фото --eve-ph = min(кадр, окно − верх фото − отступ
// до капса − самый длинный капс − 24 − «ориентир» − его низ по кадру); если фото выходит меньше 60 % кадра (низкое окно) — этапы стопкой.
function initEvening() {
  const s = document.querySelector(".s-evening");
  if (!s) return;
  const steps = [...s.querySelectorAll(".eve__step")];
  const texts = steps.map((st) => st.querySelector(".eve__text"));
  const note = s.querySelector(".eve__note");
  const probe = s.querySelector(".eve__probe");
  const track = s.querySelector(".eve__track");
  const stage = s.querySelector(".eve__stage");
  const tab = matchMedia("(min-width: 600px)");
  // По кадрам этапа 1: верх фото, фото → капс, низ «ориентира», высота фото (телефон 400:2936, планшет 400:2985)
  const M = { top: 140, gap: 36, bottom: 80, ph: 344 };
  const T = { top: 136, gap: 48, bottom: 124, ph: 576 };

  const fit = () => {
    if (reducedMotion.matches) return s.removeAttribute("data-pin");
    if (desk.matches) {
      s.style.removeProperty("--eve-ph");
      return s.setAttribute("data-pin", "");
    }
    const cw = document.documentElement.clientWidth;
    const d = tab.matches ? T : M;
    const u = tab.matches ? (cw - 64) / 770 : (Math.min(cw, 480) - 32) / 358;
    const caps = Math.max(...texts.map((t) => t.offsetHeight));
    const ph = Math.min(d.ph * u, probe.offsetHeight - (d.top + d.gap + d.bottom) * u - caps - 24 - note.offsetHeight);
    s.toggleAttribute("data-pin", ph >= 0.6 * d.ph * u);
    s.style.setProperty("--eve-ph", ph.toFixed(1) + "px");
  };

  const sw = createSwitch({ count: steps.length, loop: false, onChange: (i) => setPositions(steps, i) });
  sw.go(1, true);
  fit();
  for (const mq of [desk, tab, reducedMotion]) mq.addEventListener("change", fit);
  addEventListener("resize", fit);
  document.fonts.ready.then(fit);
  scrollSteps(track, stage, steps.length, (i) => sw.go(i), () => s.hasAttribute("data-pin"));
}

// 03: десктоп — переключатель; телефон и планшет — счётчик «0N / 03» по самой видимой карточке (IntersectionObserver по ленте)
function initMusic() {
  const s = document.querySelector(".s-music");
  if (!s) return;
  const cards = [...s.querySelectorAll(".music__card")];
  cards.forEach((c) => (c.dataset.key = c.dataset.i));
  hoverStates(s, cards, { rest: null, keep: true, click: true });

  const rail = s.querySelector(".music__rail");

  // Десктоп «в экран» (Д3а): колонки стоят от низа, H2 — × kh = min(s, (верх колонок − 24 − 104) / 296)
  const fit = () => {
    if (!desk.matches) return s.style.removeProperty("--kh");
    const u = (Math.min(document.documentElement.clientWidth, 1920) - 128) / 1312;
    const sc = Math.min(u, s.clientHeight / 900);
    s.style.setProperty("--kh", Math.min(sc, (rail.offsetTop - 128) / 296).toFixed(4) + "px");
  };
  new ResizeObserver(fit).observe(s);
  new ResizeObserver(fit).observe(rail);
  document.fonts.ready.then(fit);

  const out = s.querySelector(".music__count-n");
  const seen = new Map();
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) seen.set(e.target, e.intersectionRatio);
    let best = cards[0];
    for (const c of cards) if ((seen.get(c) || 0) > (seen.get(best) || 0)) best = c;
    const v = best.dataset.i.padStart(2, "0");
    if (out.textContent !== v) out.textContent = v;
  }, { root: rail, threshold: [0, 0.25, 0.5, 0.75, 1] });
  cards.forEach((c) => io.observe(c));
}

function initDancemaster() {
  const s = document.querySelector(".s-dancemaster");
  if (!s) return;
  const panels = [...s.querySelectorAll(".dm__panel")];
  hoverStates(s, panels, { key: (p) => p.dataset.panel });
}

function initShow() {
  const s = document.querySelector(".s-show");
  if (!s) return;
  const frames = [...s.querySelectorAll(".show__frame")];
  const words = [...s.querySelectorAll(".show__word")];
  const descs = [...s.querySelectorAll(".show__desc")];
  const list = s.querySelector(".show__tabs");
  const buttons = [...list.querySelectorAll(".show__tab")];
  const count = s.querySelector(".show__count-n");
  const track = s.querySelector(".show__track");
  const stage = s.querySelector(".show__stage");
  const n = frames.length;
  const pinned = () => desk.matches && !reducedMotion.matches;
  let t;

  // Слова неактивных форматов собираются только при входе секции — при смене они въезжают уже собранными
  words.slice(1).forEach((w) => w.querySelectorAll("[data-giant]").forEach((g) => (g.dataset.in = "")));

  const select = tabs(list, buttons, (i) => {
    if (!pinned()) return sw.go(i);
    const y = stepTop(i);
    if (y !== null) scrollTo({ top: y + 1, behavior: reducedMotion.matches ? "auto" : "smooth" });
  });

  const sw = createSwitch({
    count: n,
    onChange(i) {
      s.dataset.step = i;
      setPositions(frames, i);
      setPositions(words, i);
      descs.forEach((d, k) => {
        d.toggleAttribute("data-on", k === i - 1);
        d.setAttribute("aria-hidden", String(k !== i - 1));
      });
      select(i);
      list.style.setProperty("--i", i);
      clearTimeout(t);
      t = setTimeout(() => (count.textContent = String(i).padStart(2, "0")), reducedMotion.matches ? 0 : 600);
    },
  });

  const stepTop = scrollSteps(track, stage, n, (i) => sw.go(i), pinned);
  swipe(stage, { onNext: sw.next, onPrev: sw.prev, enabled: () => !desk.matches });
  sw.go(1, true);
}

function initAssistant() {
  const s = document.querySelector(".s-assistant");
  if (!s) return;
  hoverStates(s, [...s.querySelectorAll(".asst__item")], { rest: null, keep: true, click: true });

  // Десктоп «в экран» (Д3б): если самый длинный раскрытый ответ не помещается над «Принципом» (низкие окна),
  // «Принцип» уходит на низ фото под тень (data-tight). Меряется в обычном положении — без data-tight
  const list = s.querySelector(".asst__list");
  const answers = [...s.querySelectorAll(".asst__a")];
  const end = s.querySelector(".asst__end");
  const fit = () => {
    s.removeAttribute("data-tight");
    if (!desk.matches) return;
    const a = Math.max(...answers.map((el) => el.offsetHeight));
    s.toggleAttribute("data-tight", list.offsetTop + a + 16 > end.offsetTop);
  };
  new ResizeObserver(fit).observe(s);
  document.fonts.ready.then(fit);
}

// 07 (десктоп «в экран», Ц3): лесенка фрагментов стоит низом на экран − 102k, ступени 0 / 40k / 80k, высоты фрагментов h_i
// (метка + 12,6 + капс) — px. k — наибольшее ≤ s, при котором фрагмент 1 на 24 ниже фразы (низ 104 + 168k),
// а фрагмент 2 (и 3 — он ещё ниже) — на 24 ниже гиганта (низ 104 + 356k)
function initLessons() {
  const s = document.querySelector(".s-lessons");
  if (!s) return;
  const steps = [...s.querySelectorAll(".less__step")];
  const OFFS = [0, 40, 80];
  const fit = () => {
    if (!desk.matches) return s.style.removeProperty("--k7");
    const u = (Math.min(document.documentElement.clientWidth, 1920) - 128) / 1312;
    const h = s.clientHeight;
    const hs = steps.map((st) => st.querySelector(".less__stage").getBoundingClientRect().height + 12.6
      + st.querySelector(".less__text").getBoundingClientRect().height);
    const fits = (k) => {
      const top = h - 102 * k - Math.max(...hs.map((c, i) => OFFS[i] * k + c));
      return top >= 128 + 168 * k && top + 40 * k >= 128 + 356 * k;
    };
    let k = Math.min(u, h / 900);
    while (k > 0.3 && !fits(k)) k -= 0.005;
    s.style.setProperty("--k7", k.toFixed(4) + "px");
  };
  new ResizeObserver(fit).observe(s);
  document.fonts.ready.then(fit);
}

// 09: десктоп — наведение на правило: его «+» поворачивается, остальные правила гаснут (заметка 207:1939).
// Планшет и десктоп: правила стоят на высоте своих «+»; если на узком окне соседние наезжают, нижнее сдвигается (--nudge).
// Позиции считаются по offsetTop — без transform входа и без translate самого правила.
function initDress() {
  const s = document.querySelector(".s-dress");
  if (!s) return;
  const side = matchMedia("(min-width: 600px)");
  const figs = [...s.querySelectorAll(".dress__fig")].map((fig) => ({
    fig,
    rules: [...fig.querySelectorAll(".dress__rule")],
    marks: [...fig.querySelectorAll(".dress__rule, .dress__plus")],
  }));

  for (const { fig, rules, marks } of figs) {
    const hl = (k) => {
      k ? (fig.dataset.hl = k) : delete fig.dataset.hl;
      marks.forEach((el) => el.toggleAttribute("data-on", el.dataset.k === k));
    };
    rules.forEach((r) => {
      r.addEventListener("pointerenter", (e) => e.pointerType === "mouse" && desk.matches && hl(r.dataset.k));
      r.addEventListener("pointerleave", (e) => e.pointerType === "mouse" && hl(null));
    });
  }

  const layout = () => {
    for (const { rules } of figs) {
      rules.forEach((r) => r.style.removeProperty("--nudge"));
      if (!side.matches) continue;
      let bottom = -Infinity;
      for (const r of rules) {
        const h = r.offsetHeight;
        const dy = desk.matches ? parseFloat(getComputedStyle(r).getPropertyValue("--dy")) || -9 : -h / 2;
        const top = r.offsetTop + dy;
        const nudge = Math.max(0, bottom + 8 - top);
        if (nudge) r.style.setProperty("--nudge", nudge.toFixed(1) + "px");
        bottom = top + nudge + h;
      }
    }
  };
  let t;
  addEventListener("resize", () => {
    clearTimeout(t);
    t = setTimeout(layout, 100);
  });
  document.fonts.ready.then(layout);
  layout();

  // Десктоп (Д3в, 09 A): экран фигур — после «Мы поможем»; k фигур (--k9) = min(s, (экран − 168) / 878, (экран − 168 − продолжение) / 813),
  // третья колонка «Мы поможем» — не выше низа второй (--o3). После смены k правила раскладываются заново
  const help = s.querySelector(".dress__help");
  const svc2 = s.querySelector(".dress__svc li:nth-child(2)");
  const cont = s.querySelector(".dress__wc");
  const fit = () => {
    if (!desk.matches) return ["--k9", "--o3"].forEach((p) => s.style.removeProperty(p));
    const u = (Math.min(document.documentElement.clientWidth, 1920) - 128) / 1312;
    const h = s.clientHeight - help.offsetTop - help.offsetHeight;
    const sc = Math.min(u, h / 900);
    s.style.setProperty("--o3", Math.max(98 * sc, 40 * sc + svc2.offsetHeight + 4).toFixed(2) + "px");
    s.style.setProperty("--k9", Math.min(sc, (h - 168) / 878, (h - 168 - cont.offsetHeight) / 813).toFixed(4) + "px");
    layout();
  };
  new ResizeObserver(fit).observe(s);
  document.fonts.ready.then(fit);
}

// 10: смена вечеров (switch.js). Новый вечер всегда открывается «вперёд», и по кругу назад тоже: его слои без перехода встают в after
// (data-jump), затем открываются; прежние уходят в before. Телефон и планшет — свайп по главному слоту и тап по пункту, автосмены нет;
// десктоп — автосмена 4 с, пауза при наведении на пункты, сцену и описание, при фокусе внутри, вне экрана и при reduced-motion;
// после первого выбора пользователем (клик, клавиатура, свайп) автосмена останавливается насовсем.
// Пока идёт смена (1,2 с), новая не принимается.
function initEvenings() {
  const s = document.querySelector(".s-eves");
  if (!s) return;
  const layers = [...s.querySelectorAll(".eves__frame, .eves__word, .eves__panel")];
  const list = s.querySelector(".eves__tabs");
  const buttons = [...list.querySelectorAll(".eves__tab")];
  const mark = s.querySelector(".eves__mark");
  const count = s.querySelector(".eves__count-n");
  const zones = [s.querySelector(".eves__body"), s.querySelector(".eves__info")];
  const n = s.querySelectorAll(".eves__panel").length;
  let busy = false;
  let stopped = false;
  let t;

  // Слова неактивных вечеров собираются только при входе секции — при смене они въезжают уже собранными
  s.querySelectorAll('.eves__word:not([data-i="1"]) [data-giant]').forEach((g) => (g.dataset.in = ""));

  const placeMark = (i) => {
    const r = buttons[i - 1].firstElementChild.getClientRects()[0];
    if (r) mark.style.setProperty("--mark-y", (r.top + r.height / 2 - list.getBoundingClientRect().top - 0.5).toFixed(1) + "px");
  };

  const pick = (i) => {
    stopped = true;
    go(i);
  };
  const select = tabs(list, buttons, pick);

  const sw = createSwitch({
    count: n,
    onChange(i) {
      busy = true;
      setTimeout(() => (busy = false), reducedMotion.matches ? 200 : 1200);
      for (const el of layers) {
        if (Number(el.dataset.i) !== i) continue;
        el.dataset.jump = "";
        el.dataset.pos = "after";
      }
      void s.offsetWidth;
      for (const el of layers) {
        if (Number(el.dataset.i) === i) {
          delete el.dataset.jump;
          el.dataset.pos = "active";
        } else if (el.dataset.pos === "active") {
          el.dataset.pos = "before";
        } else {
          el.dataset.jump = "";
          el.dataset.pos = "after";
        }
      }
      s.dataset.step = i;
      select(i);
      placeMark(i);
      clearTimeout(t);
      t = setTimeout(() => (count.textContent = String(i).padStart(2, "0")), reducedMotion.matches ? 0 : 200);
    },
  });

  function go(i) {
    if (busy) return select(sw.index);
    sw.go(i);
    tick();
  }

  swipe(s.querySelector('.eves__slot[data-slot="b"]'), { onNext: () => pick(sw.index + 1), onPrev: () => pick(sw.index - 1) });

  // Автосмена (только десктоп)
  let auto = 0;
  let seen = false;
  let over = 0;
  let focus = false;
  function tick() {
    clearTimeout(auto);
    if (desk.matches && !reducedMotion.matches && !stopped && seen && !over && !focus && !document.hidden) {
      auto = setTimeout(() => go(sw.index + 1), 4000);
    }
  }
  new IntersectionObserver(([e]) => {
    seen = e.isIntersecting;
    tick();
  }, { threshold: 0.3 }).observe(zones[0]);
  for (const z of zones) {
    z.addEventListener("pointerenter", (e) => e.pointerType === "mouse" && (over++, tick()));
    z.addEventListener("pointerleave", (e) => e.pointerType === "mouse" && ((over = Math.max(0, over - 1)), tick()));
  }
  s.addEventListener("focusin", () => ((focus = true), tick()));
  s.addEventListener("focusout", (e) => !s.contains(e.relatedTarget) && ((focus = false), tick()));
  document.addEventListener("visibilitychange", tick);
  desk.addEventListener("change", tick);
  reducedMotion.addEventListener("change", tick);

  let r;
  addEventListener("resize", () => {
    clearTimeout(r);
    r = setTimeout(() => placeMark(sw.index), 100);
  });
  document.fonts.ready.then(() => placeMark(sw.index));
  placeMark(1);

  // Десктоп (Д3в, 10 B): тело — экран под шапкой. Самая длинная суть низом на экран − 48 (--tt), k коллажа (--k10) = min(s, (--tt − 184) / 600),
  // слот A — не выше низа пунктов + 16 (--a-min; пункт «Кашемир» на узком окне — в три строки)
  const body = s.querySelector(".eves__body");
  const nav = s.querySelector(".eves__nav");
  const descs = [...s.querySelectorAll(".eves__desc")];
  const fit = () => {
    if (!desk.matches) return ["--tt", "--k10", "--a-min"].forEach((p) => s.style.removeProperty(p));
    const u = (Math.min(document.documentElement.clientWidth, 1920) - 128) / 1312;
    const h = body.offsetHeight;
    const tt = h - 48 - Math.max(...descs.map((d) => d.offsetHeight));
    s.style.setProperty("--tt", tt.toFixed(1) + "px");
    s.style.setProperty("--k10", Math.min(u, h / 900, (tt - 184) / 600).toFixed(4) + "px");
    s.style.setProperty("--a-min", (nav.offsetTop + nav.offsetHeight - 4.5 + 16).toFixed(1) + "px");
  };
  new ResizeObserver(fit).observe(s);
  document.fonts.ready.then(fit);
}

// 11–12 Финал (десктоп, Ц4): низ — px от низа экрана, верх — k от линии 104. --y1 — верх капса фразы: капс низом на 116
// (28 над ссылкой), но фраза (низ --y1 + 108k) не ниже 32 над контактами (экран − 48) — при k > 1 капс и фраза поднимаются.
// k (--k12) — наибольшее ≤ s (шаг 0,005), при котором команда (низ 104 + 416k + её высота) на 24 выше фразы (--y1 − 12k)
function initFinale() {
  const s = document.querySelector(".s-finale");
  if (!s) return;
  const team = s.querySelector(".fin__team");
  const more = s.querySelector(".fin__more");
  const fit = () => {
    if (!desk.matches) return ["--k12", "--y1"].forEach((p) => s.style.removeProperty(p));
    const u = (Math.min(document.documentElement.clientWidth, 1920) - 128) / 1312;
    const h = s.clientHeight;
    const ht = team.offsetHeight;
    const y1 = (k) => Math.min(h - 116 - more.offsetHeight, h - 80 - 108 * k);
    let k = Math.min(u, h / 900);
    while (k > 0.2 && 128 + 416 * k + ht > y1(k) - 12 * k) k -= 0.005;
    s.style.setProperty("--y1", y1(k).toFixed(1) + "px");
    s.style.setProperty("--k12", k.toFixed(4) + "px");
  };
  new ResizeObserver(fit).observe(s);
  document.fonts.ready.then(fit);
}

// Каждый блок отдельно: ошибка в одном не останавливает остальные
export function initBlocks() {
  for (const init of [initPrep, initEvening, initMusic, initDancemaster, initShow, initAssistant, initLessons, initDress, initEvenings, initFinale]) {
    try {
      init();
    } catch (err) {
      console.error(err);
    }
  }
}
