/* =====================================================================
   РЕЖИМ ПРАВОК — комментарии к элементам прямо на макете
   =====================================================================

   Отдельный файл, а не часть script.js: этот код к сайту отношения не
   имеет и перед сдачей удаляется одной строкой из index.html. Пока он
   подключён, на боевую страницу он всё равно не влияет — режим спит,
   пока в адресе нет ?review=1.

   КАК ПОЛЬЗОВАТЬСЯ
     1. Открыть index.html?review=1
     2. Навести мышь — элемент под курсором подсвечивается рамкой.
        Клик — открывается поле, пишем правку, Ctrl+Enter — сохранить.
     3. Метки висят на странице, копятся в localStorage и переживают
        перезагрузку. Панель справа — список всех правок.
     4. «Скачать» кладёт review-comments.json в загрузки. Дальше я читаю
        этот файл и вношу правки.

   ГОРЯЧИЕ КЛАВИШИ
     C        — выключить/включить режим выбора (чтобы кликать по сайту)
     Esc      — закрыть поле ввода
     Ctrl+Enter — сохранить комментарий

   ЧТО ЗАПИСЫВАЕТСЯ В КОММЕНТАРИЙ
     selector — CSS-путь до элемента, по нему я нахожу место в вёрстке;
     section  — id секции, в которой сидит элемент (человеческий адрес);
     text     — сам текст элемента, обрезанный: по нему видно, о чём речь,
                даже если вёрстка с тех пор поменялась;
     note     — то, что написали вы.
   ===================================================================== */

(function () {
  'use strict';

  // Режим включается только явным флагом в адресе. Без него файл
  // выходит здесь же и ничего не делает — ни слушателей, ни разметки.
  var params = new URLSearchParams(location.search);
  if (params.get('review') !== '1') return;

  var STORAGE_KEY = 'review-comments-v1';

  /* ---------------------------------------------------------------
     ХРАНИЛИЩЕ
     localStorage привязан к origin. При открытии файла по file://
     часть браузеров запрещает к нему доступ и кидает исключение —
     поэтому каждое обращение обёрнуто, и при отказе режим просто
     работает без сохранения между перезагрузками.
     --------------------------------------------------------------- */
  var comments = [];

  function load() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      comments = raw ? JSON.parse(raw) : [];
    } catch (e) {
      comments = [];
    }
  }

  function save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(comments));
    } catch (e) {
      /* приватный режим или file:// — молча продолжаем без записи */
    }
  }

  /* ---------------------------------------------------------------
     АДРЕС ЭЛЕМЕНТА
     Задача — получить строку, по которой элемент находится в коде
     однозначно и при этом читаемо. Порядок предпочтений:
     id → уникальный класс → путь с :nth-of-type от ближайшего предка
     с id. Путь обрывается на первом id, иначе селекторы вырастают
     до десятка звеньев и в них невозможно ничего разглядеть.
     --------------------------------------------------------------- */
  function cssPath(el) {
    if (!el || el.nodeType !== 1) return '';
    if (el.id) return '#' + CSS.escape(el.id);

    var parts = [];
    var node = el;

    while (node && node.nodeType === 1 && node !== document.body) {
      var step = node.tagName.toLowerCase();

      if (node.id) {
        parts.unshift('#' + CSS.escape(node.id));
        break;
      }

      // Класс берём один и только если он в документе единственный:
      // из-за утилитарных классов вроде t-body селектор иначе
      // указывал бы на полсотни элементов сразу.
      var cls = Array.prototype.find.call(node.classList || [], function (c) {
        try {
          return document.querySelectorAll('.' + CSS.escape(c)).length === 1;
        } catch (e) {
          return false;
        }
      });

      if (cls) {
        step += '.' + CSS.escape(cls);
      } else {
        // Считаем позицию среди соседей того же тега — nth-of-type
        // устойчивее nth-child: соседние текстовые узлы и комментарии
        // на нумерацию не влияют.
        var parent = node.parentNode;
        if (parent) {
          var same = Array.prototype.filter.call(parent.children, function (s) {
            return s.tagName === node.tagName;
          });
          if (same.length > 1) {
            step += ':nth-of-type(' + (same.indexOf(node) + 1) + ')';
          }
        }
      }

      parts.unshift(step);
      node = node.parentNode;
    }

    return parts.join(' > ');
  }

  // Человеческий адрес: id ближайшей секции. Именно его удобно
  // читать в списке правок — «#music» понятнее, чем длинный путь.
  function sectionOf(el) {
    var s = el.closest('section[id], header[id], footer, [id]');
    while (s && !s.id) s = s.parentElement ? s.parentElement.closest('[id]') : null;
    return s && s.id ? '#' + s.id : '—';
  }

  function shortText(el) {
    var t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    return t.length > 80 ? t.slice(0, 80) + '…' : t;
  }

  /* ---------------------------------------------------------------
     РАЗМЕТКА ОВЕРЛЕЯ
     Всё кладётся в один контейнер с id review-ui: так его легко
     исключить из выбора (клики по самой панели не должны
     восприниматься как клики по сайту) и целиком снести при выходе.
     --------------------------------------------------------------- */
  var ui = document.createElement('div');
  ui.id = 'review-ui';
  ui.innerHTML = [
    '<div class="rv-hl" hidden></div>',

    '<div class="rv-panel">',
    '  <div class="rv-panel__head">',
    '    <span class="rv-panel__title">Правки</span>',
    '    <span class="rv-count">0</span>',
    '  </div>',
    '  <div class="rv-hint">Клик по элементу — оставить правку. <b>C</b> — пауза выбора.</div>',
    '  <ul class="rv-list"></ul>',
    '  <div class="rv-panel__foot">',
    '    <button type="button" class="rv-btn rv-btn--main" data-act="export">Скачать JSON</button>',
    '    <button type="button" class="rv-btn" data-act="copy">Копировать</button>',
    '    <button type="button" class="rv-btn rv-btn--ghost" data-act="clear">Очистить</button>',
    '  </div>',
    '</div>',

    '<div class="rv-pop" hidden>',
    '  <div class="rv-pop__target"></div>',
    '  <textarea class="rv-pop__input" rows="3" placeholder="Что поправить?"></textarea>',
    '  <div class="rv-pop__foot">',
    '    <span class="rv-pop__hint">Ctrl+Enter — сохранить</span>',
    '    <button type="button" class="rv-btn rv-btn--main" data-act="add">Добавить</button>',
    '  </div>',
    '</div>',

    '<div class="rv-toggle" title="Пауза выбора — клавиша C">Выбор: <b>вкл</b></div>'
  ].join('');
  document.body.appendChild(ui);

  var hl = ui.querySelector('.rv-hl');
  var pop = ui.querySelector('.rv-pop');
  var popTarget = ui.querySelector('.rv-pop__target');
  var input = ui.querySelector('.rv-pop__input');
  var list = ui.querySelector('.rv-list');
  var counter = ui.querySelector('.rv-count');
  var toggle = ui.querySelector('.rv-toggle');

  var picking = true;   // режим выбора элемента активен
  var current = null;   // элемент, к которому пишем правку

  /* ---------------------------------------------------------------
     ПОДСВЕТКА ПОД КУРСОРОМ
     Рамка рисуется отдельным блоком поверх страницы, а не через
     outline на самом элементе: outline сдвигал бы вёрстку в местах
     с плотными сетками и мешал бы смотреть на макет.
     --------------------------------------------------------------- */
  function moveHl(el) {
    var r = el.getBoundingClientRect();
    hl.style.transform = 'translate(' + r.left + 'px,' + r.top + 'px)';
    hl.style.width = r.width + 'px';
    hl.style.height = r.height + 'px';
    hl.hidden = false;
  }

  document.addEventListener('mousemove', function (e) {
    if (!picking || !pop.hidden) return;
    var el = e.target;
    if (!el || ui.contains(el)) { hl.hidden = true; return; }
    moveHl(el);
  }, true);

  /* ---------------------------------------------------------------
     КЛИК ПО ЭЛЕМЕНТУ
     Перехватываем на фазе погружения и глушим: иначе клик уехал бы
     в обработчики сайта — открылось бы меню, переключился таб,
     ушла бы отправка формы.
     --------------------------------------------------------------- */
  document.addEventListener('click', function (e) {
    if (!picking) return;
    if (ui.contains(e.target)) return;

    e.preventDefault();
    e.stopPropagation();

    current = e.target;
    openPop(e.clientX, e.clientY);
  }, true);

  function openPop(x, y) {
    popTarget.textContent = sectionOf(current) + ' · ' + shortText(current);
    input.value = '';
    pop.hidden = false;

    // Держим окно в пределах экрана: у нижнего края оно
    // разворачивается вверх, у правого — влево.
    var w = 300, h = 150;
    var left = Math.min(x + 12, window.innerWidth - w - 12);
    var top = y + 12 + h > window.innerHeight ? y - h - 12 : y + 12;
    pop.style.left = Math.max(12, left) + 'px';
    pop.style.top = Math.max(12, top) + 'px';

    input.focus();
  }

  function closePop() {
    pop.hidden = true;
    current = null;
  }

  function addComment() {
    var note = input.value.trim();
    if (!note || !current) return;

    comments.push({
      id: Date.now(),
      section: sectionOf(current),
      selector: cssPath(current),
      tag: current.tagName.toLowerCase(),
      text: shortText(current),
      note: note
    });

    save();
    render();
    closePop();
  }

  /* ---------------------------------------------------------------
     СПИСОК ПРАВОК
     Перерисовывается целиком: правок здесь десятки, не тысячи, —
     точечные обновления усложнили бы код без выигрыша.
     --------------------------------------------------------------- */
  function render() {
    counter.textContent = comments.length;
    list.innerHTML = '';

    comments.forEach(function (c, i) {
      var li = document.createElement('li');
      li.className = 'rv-item';
      li.innerHTML =
        '<div class="rv-item__head">' +
        '  <span class="rv-item__n">' + (i + 1) + '</span>' +
        '  <span class="rv-item__sec"></span>' +
        '  <button type="button" class="rv-item__del" title="Удалить">×</button>' +
        '</div>' +
        '<div class="rv-item__note"></div>';

      // Текст ставим через textContent, а не в шаблон: правка может
      // содержать угловые скобки, и в innerHTML они поломали бы разметку.
      li.querySelector('.rv-item__sec').textContent = c.section;
      li.querySelector('.rv-item__note').textContent = c.note;

      li.querySelector('.rv-item__del').addEventListener('click', function (e) {
        e.stopPropagation();
        comments = comments.filter(function (x) { return x.id !== c.id; });
        save();
        render();
      });

      // Клик по карточке — прокрутка к элементу и вспышка рамкой,
      // чтобы в длинном списке не терять, о чём была правка.
      li.addEventListener('click', function () {
        var el;
        try { el = document.querySelector(c.selector); } catch (err) { el = null; }
        if (!el) return;
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(function () {
          moveHl(el);
          hl.classList.add('rv-hl--flash');
          setTimeout(function () { hl.classList.remove('rv-hl--flash'); }, 900);
        }, 400);
      });

      list.appendChild(li);
    });
  }

  /* ---------------------------------------------------------------
     ВЫГРУЗКА
     --------------------------------------------------------------- */
  function payload() {
    return JSON.stringify({
      page: location.pathname.split('/').pop() || 'index.html',
      date: new Date().toISOString(),
      comments: comments
    }, null, 2);
  }

  function exportFile() {
    var blob = new Blob([payload()], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'review-comments.json';
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  }

  function copyAll(btn) {
    var done = function () {
      var old = btn.textContent;
      btn.textContent = 'Скопировано';
      setTimeout(function () { btn.textContent = old; }, 1200);
    };
    // Буфер обмена по file:// недоступен — на этот случай
    // подстраховка через скрытое поле и execCommand.
    if (navigator.clipboard && location.protocol !== 'file:') {
      navigator.clipboard.writeText(payload()).then(done);
    } else {
      var ta = document.createElement('textarea');
      ta.value = payload();
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { /* ничего */ }
      ta.remove();
    }
  }

  /* ---------------------------------------------------------------
     УПРАВЛЕНИЕ
     --------------------------------------------------------------- */
  ui.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-act]');
    if (!btn) return;
    var act = btn.dataset.act;

    if (act === 'add') addComment();
    if (act === 'export') exportFile();
    if (act === 'copy') copyAll(btn);
    if (act === 'clear') {
      if (confirm('Удалить все правки?')) {
        comments = [];
        save();
        render();
      }
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !pop.hidden) { closePop(); return; }

    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey) && !pop.hidden) {
      e.preventDefault();
      addComment();
      return;
    }

    // Переключатель режима выбора. Проверяем, что фокус не в поле
    // ввода, иначе буква «c» в тексте правки выключала бы режим.
    var typing = /input|textarea/i.test((e.target.tagName || ''));
    if ((e.key === 'c' || e.key === 'с') && !typing && !e.ctrlKey && !e.metaKey) {
      picking = !picking;
      toggle.innerHTML = 'Выбор: <b>' + (picking ? 'вкл' : 'выкл') + '</b>';
      toggle.classList.toggle('rv-toggle--off', !picking);
      if (!picking) hl.hidden = true;
    }
  });

  toggle.addEventListener('click', function () {
    picking = !picking;
    toggle.innerHTML = 'Выбор: <b>' + (picking ? 'вкл' : 'выкл') + '</b>';
    toggle.classList.toggle('rv-toggle--off', !picking);
    if (!picking) hl.hidden = true;
  });

  // Рамка привязана к координатам окна, а не документа: при прокрутке
  // и смене размера она уезжает, поэтому просто прячем её.
  window.addEventListener('scroll', function () { hl.hidden = true; }, true);
  window.addEventListener('resize', function () { hl.hidden = true; });

  load();
  render();
})();
