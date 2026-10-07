// Переключатель «один из N» (05 Шоу, дальше 10 Вечера): шаг, положения слоёв, пункты-вкладки, свайп, шаги по прокрутке.
//
//   const sw = createSwitch({ count, loop, onChange(n, from) })   — sw.go(n), sw.next(), sw.prev(), sw.index
//   setPositions(nodes, n)       — data-pos у слоёв с data-i: before / active / after (CSS рисует занавес и барабан)
//   tabs(list, buttons, onPick)  — role="tab": клик, стрелки ← → и Home / End, aria-selected и roving tabindex — select(n)
//   swipe(el, { onNext, onPrev }) — горизонтальный жест ≥ 40 px (влево — вперёд); вертикальный скролл не перехватывается
//                                   (у el в CSS touch-action: pan-y)
//   scrollSteps(track, stage, count, onStep) — шаг = ближайшее положение закреплённой сцены на дорожке (как 02),
//                                   возвращает stepTop(n) — прокрутка, на которой стоит шаг n

export function createSwitch({ count, loop = true, start = 1, onChange }) {
  let index = start;
  const go = (n, force = false) => {
    n = loop ? ((n - 1 + count) % count) + 1 : Math.min(count, Math.max(1, n));
    if (n === index && !force) return;
    const from = index;
    index = n;
    onChange(n, from);
  };
  return {
    go,
    next: () => go(index + 1),
    prev: () => go(index - 1),
    get index() {
      return index;
    },
  };
}

export function setPositions(nodes, n) {
  for (const el of nodes) {
    const i = Number(el.dataset.i);
    el.dataset.pos = i < n ? "before" : i === n ? "active" : "after";
  }
}

export function tabs(list, buttons, onPick) {
  const select = (n) => {
    buttons.forEach((b, i) => {
      const on = i === n - 1;
      b.setAttribute("aria-selected", String(on));
      b.tabIndex = on ? 0 : -1;
    });
  };
  buttons.forEach((b, i) => b.addEventListener("click", () => onPick(i + 1)));
  list.addEventListener("keydown", (e) => {
    const cur = buttons.indexOf(document.activeElement);
    if (cur < 0) return;
    const last = buttons.length - 1;
    const to = { ArrowRight: cur + 1, ArrowDown: cur + 1, ArrowLeft: cur - 1, ArrowUp: cur - 1, Home: 0, End: last }[e.key];
    if (to === undefined) return;
    e.preventDefault();
    const n = (to + buttons.length) % buttons.length;
    buttons[n].focus();
    onPick(n + 1);
  });
  return select;
}

export function swipe(el, { onNext, onPrev, threshold = 40, enabled = () => true }) {
  let x = 0;
  let y = 0;
  let id = null;
  el.addEventListener("pointerdown", (e) => {
    if (!e.isPrimary || e.pointerType === "mouse" || !enabled()) return;
    id = e.pointerId;
    x = e.clientX;
    y = e.clientY;
  });
  const end = (e) => {
    if (e.pointerId !== id) return;
    id = null;
    const dx = e.clientX - x;
    const dy = e.clientY - y;
    if (Math.abs(dx) < threshold || Math.abs(dx) < Math.abs(dy)) return;
    dx < 0 ? onNext() : onPrev();
  };
  el.addEventListener("pointerup", end);
  // Браузер забрал жест себе (вертикальный скролл) — жест не засчитывается
  el.addEventListener("pointercancel", () => (id = null));
}

export function scrollSteps(track, stage, count, onStep, active = () => true) {
  const progress = () => {
    const r = track.getBoundingClientRect();
    const travel = r.height - stage.offsetHeight;
    if (travel <= 0) return null;
    const top = parseFloat(getComputedStyle(stage).top) || 0;
    return { p: Math.min(1, Math.max(0, (top - r.top) / travel)), travel, top, abs: r.top + scrollY };
  };
  let raf = 0;
  const check = () => {
    raf = 0;
    if (!active()) return;
    const pr = progress();
    if (pr) onStep(1 + Math.round(pr.p * (count - 1)));
  };
  const schedule = () => raf || (raf = requestAnimationFrame(check));
  addEventListener("scroll", schedule, { passive: true });
  addEventListener("resize", schedule);
  check();
  // Прокрутка, на которой стоит шаг n (смена шага — на полпути между соседними)
  return (n) => {
    const pr = progress();
    if (!pr) return null;
    return pr.abs - pr.top + ((n - 1) / (count - 1)) * pr.travel;
  };
}
