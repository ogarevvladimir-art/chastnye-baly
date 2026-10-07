// Состояния десктопа по наведению (приём пилота, ОБЩЕЕ «Приёмы пилота»): data-state на секции, data-on у активной части.
// Мышь — наведение на часть; клавиатура — фокус внутри части (части получают tabindex на десктопе);
// касание на широком экране без мыши — тап по части. На телефоне и планшете состояний нет — секция в покое.
//
//   hoverStates(section, parts, { key, rest, keep, click })
//     key(part)  — имя состояния части (по умолчанию part.dataset.key);
//     rest       — состояние покоя (null — покоя нет, часть остаётся выбранной: 03 Музыка);
//     keep       — не возвращаться в покой, когда курсор ушёл;
//     click      — клик мышью тоже выбирает часть (03: «клик по неактивной колонке»).

const desk = matchMedia("(min-width: 1024px)");
const fine = matchMedia("(hover: hover) and (pointer: fine)");

export function hoverStates(section, parts, { key = (p) => p.dataset.key, rest = "rest", keep = false, click = false } = {}) {
  if (!section || !parts.length) return;
  const initial = rest ?? key(parts[0]);

  const set = (state) => {
    if (!desk.matches) state = initial;
    section.dataset.state = state;
    for (const p of parts) p.toggleAttribute("data-on", desk.matches && key(p) === state && state !== rest);
  };

  const tabs = () => parts.forEach((p) => (desk.matches ? (p.tabIndex = 0) : p.removeAttribute("tabindex")));

  for (const p of parts) {
    p.addEventListener("pointerenter", (e) => {
      if (e.pointerType === "mouse") set(key(p));
    });
    p.addEventListener("focusin", () => set(key(p)));
    p.addEventListener("click", (e) => {
      if (!desk.matches || e.target.closest("a")) return;
      if (fine.matches) {
        if (click) set(key(p));
        return;
      }
      set(section.dataset.state === key(p) && rest !== null ? rest : key(p));
    });
  }

  if (!keep && rest !== null) {
    const zone = parts[0].parentElement;
    zone.addEventListener("pointerleave", (e) => {
      if (e.pointerType === "mouse" && !zone.contains(document.activeElement)) set(rest);
    });
    zone.addEventListener("focusout", (e) => {
      if (!zone.contains(e.relatedTarget) && !zone.matches(":hover")) set(rest);
    });
  }

  desk.addEventListener("change", () => {
    tabs();
    set(initial);
  });
  tabs();
  set(initial);
}
