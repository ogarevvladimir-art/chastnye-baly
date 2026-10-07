import React from 'react';

/* Логотип «Plyaskin Events» — PNG с прозрачным фоном, знак набран золотисто-охристой
   антиквой в две строки. Присланный файл — единственная версия знака.

   Путь к файлу считается от тега <script src=".../_ds_bundle.js">, чтобы знак
   находился с любой страницы-потребителя; при необходимости передайте src вручную. */
const LOGO_PATH = 'assets/logo-plyaskin-events.png';

function resolveLogo() {
  try {
    const tag = Array.from(document.querySelectorAll('script[src]')).find((s) =>
      s.getAttribute('src').indexOf('_ds_bundle.js') >= 0
    );
    if (tag) return new URL(LOGO_PATH, new URL(tag.src, document.baseURI)).href;
  } catch (e) {}
  return LOGO_PATH;
}

export function Logo({ height = 56, src, alt = 'Plyaskin Events', style, ...rest }) {
  const url = React.useMemo(() => src || resolveLogo(), [src]);
  return <img src={url} alt={alt} style={{ height, width: 'auto', display: 'block', ...style }} {...rest} />;
}
