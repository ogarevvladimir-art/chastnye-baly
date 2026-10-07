import React from 'react';

/* Логотипа в исходных материалах нет — знак бренда это набор антиквой.
   Значения сняты с шапки макета: Old Standard TT 24px, трекинг −1px. */
export function Wordmark({ size = 24, tone = 'default', style, ...rest }) {
  return (
    <span
      style={{
        fontFamily: 'var(--font-display)',
        fontWeight: 400,
        fontSize: size,
        lineHeight: 1,
        letterSpacing: size >= 60 ? '-4px' : '-1px',
        whiteSpace: 'nowrap',
        color: tone === 'on-brand' ? 'rgba(171,167,154,0.95)' : 'var(--greige-90)',
        ...style,
      }}
      {...rest}
    >
      Частные&nbsp;балы
    </span>
  );
}
