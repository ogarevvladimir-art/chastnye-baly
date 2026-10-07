// Лист формы (этап 5 — интерфейс; отправка — этап 6). <dialog> + showModal(): растворение 0,45 с, фокус встаёт в поле, по которому
// тапнули (data-form="name | phone | message"); открыватель без поля (пусто) — фокус на заголовке листа, без экранной клавиатуры.
// Esc и «×» закрывают и возвращают фокус на открыватель.
// Скролл страницы заблокирован (html.is-locked, как у меню). Открыватели — все [data-form]: «→ обсудить вечер», «Обсудить … →»,
// «→ оставить заявку», «Связаться» в шапке, меню и подвале, поля и «→ отправить» панели-затвора; data-format — формат в скрытое поле.
// Фокус с клавиатуры — html[data-kbd] (у поля линия 2 px), мышью и пальцем — без подсветки.
// Отправка пока имитируется: проверка полей → 0,8 с → «Заявка отправлена»; адрес с ?form=error — имитация сбоя.
// Тексты ошибок, сбоя и «отправлено» — заглушки (data-stub), ждут текста заказчика.

import { reducedMotion } from "./motion.js";

const FADE = 450;

export function initForm() {
  const html = document.documentElement;
  const sheet = document.getElementById("form");
  if (!sheet) return;
  // Без <dialog> (iOS до 15.4) лист остаётся на странице, как без JS; ссылки ведут к нему якорем
  if (typeof sheet.showModal !== "function") {
    html.classList.add("no-dialog");
    return;
  }

  const form = sheet.querySelector("form");
  const fields = { name: form.elements.name, phone: form.elements.phone, message: form.elements.message };
  const format = form.elements.format;
  const viewForm = sheet.querySelector('[data-view="form"]');
  const viewDone = sheet.querySelector('[data-view="done"]');
  const fail = sheet.querySelector(".sheet__fail");
  const heading = sheet.querySelector("#form-h");
  const simulateError = new URLSearchParams(location.search).get("form") === "error";
  let opener = null;
  let closing = 0;

  const rules = {
    name: (v) => v.trim().length > 0,
    phone: (v) => v.replace(/\D/g, "").length >= 10,
  };

  const check = (key) => {
    const el = fields[key];
    const ok = rules[key](el.value);
    const box = el.closest(".field");
    box.toggleAttribute("data-invalid", !ok);
    el.setAttribute("aria-invalid", String(!ok));
    box.querySelector(".field__err").hidden = ok;
    return ok;
  };

  // «Несколько слов» — три строки и растёт с текстом
  const grow = () => {
    const ta = fields.message;
    ta.style.height = "";
    if (ta.scrollHeight > ta.clientHeight) ta.style.height = ta.scrollHeight + 1 + "px";
  };

  const reset = () => {
    form.reset();
    viewForm.hidden = false;
    viewDone.hidden = true;
    fail.hidden = true;
    for (const key of Object.keys(rules)) {
      fields[key].closest(".field").removeAttribute("data-invalid");
      fields[key].removeAttribute("aria-invalid");
      fields[key].closest(".field").querySelector(".field__err").hidden = true;
    }
    grow();
  };

  function open(key, from, fmt) {
    clearTimeout(closing);
    opener = from;
    format.value = fmt || "";
    if (!viewDone.hidden) reset();
    if (!sheet.open) sheet.showModal();
    html.classList.add("is-locked", "is-sheet");
    (fields[key] || heading).focus({ preventScroll: true });
    requestAnimationFrame(() => (sheet.dataset.state = "open"));
  }

  function close() {
    if (!sheet.open || sheet.dataset.state !== "open") return;
    delete sheet.dataset.state;
    html.classList.remove("is-locked", "is-sheet");
    closing = setTimeout(() => {
      sheet.close();
      // Открыватель в закрытом меню (inert) или скрытый — фокус на кнопку «Меню»
      const back = opener?.isConnected && !opener.closest("[inert]") && opener.getClientRects().length ? opener
        : document.querySelector(".site-header__menu");
      back?.focus({ preventScroll: true });
    }, reducedMotion.matches ? 0 : FADE);
  }

  document.addEventListener("click", (e) => {
    const a = e.target.closest("[data-form]");
    if (!a || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault();
    open(a.dataset.form, a, a.dataset.format);
  });

  sheet.querySelector(".sheet__close").addEventListener("click", close);
  sheet.addEventListener("cancel", (e) => {
    e.preventDefault();
    close();
  });
  // Лист закрыт браузером в обход close() — снять блокировку
  sheet.addEventListener("close", () => {
    delete sheet.dataset.state;
    html.classList.remove("is-locked", "is-sheet");
  });

  // Модальность ввода: Tab (и Enter / пробел вне полей) — клавиатура, касание или мышь — нет
  addEventListener("keydown", (e) => {
    const typing = e.target.matches?.("input, textarea");
    if (e.key === "Tab" || (!typing && (e.key === "Enter" || e.key === " "))) html.dataset.kbd = "";
  }, true);
  addEventListener("pointerdown", () => delete html.dataset.kbd, true);

  // Поле в фокусе при открытой экранной клавиатуре — в видимую часть листа
  sheet.addEventListener("focusin", (e) => {
    if (!e.target.matches(".field__in")) return;
    setTimeout(() => {
      const vv = window.visualViewport;
      if (vv && vv.height < innerHeight - 80) e.target.scrollIntoView({ block: "center", behavior: reducedMotion.matches ? "auto" : "smooth" });
    }, 300);
  });

  fields.message.addEventListener("input", grow);
  for (const key of Object.keys(rules)) {
    fields[key].addEventListener("input", () => fields[key].closest(".field").hasAttribute("data-invalid") && check(key));
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (sheet.hasAttribute("data-sending")) return;
    fail.hidden = true;
    const bad = Object.keys(rules).filter((key) => !check(key));
    if (bad.length) {
      fields[bad[0]].focus();
      return;
    }
    sheet.dataset.sending = "";
    setTimeout(() => {
      delete sheet.dataset.sending;
      if (simulateError) {
        fail.hidden = false;
        return;
      }
      viewForm.hidden = true;
      viewDone.hidden = false;
      viewDone.querySelector("[tabindex]").focus();
    }, 800);
  });
}
