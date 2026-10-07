import React from 'react';

/* Метка секции и нумерация: Гротеск 500, трекинг 2.34px, 13px.
   Единственное место, где терракота появляется в тексте.
   Поверх Terra терракота не читается — там метка идёт greige 70%. */
export function SectionLabel({ number, children, tone = 'accent', style, ...rest }) {
  const text = [number, children].filter(Boolean);
  return (
    <div
      style={{
        fontFamily: 'var(--font-sans)',
        fontSize: 'var(--number-size)',
        fontWeight: 'var(--number-weight)',
        lineHeight: 'var(--number-leading)',
        letterSpacing: 'var(--number-tracking)',
        color: tone === 'accent' ? 'var(--text-accent)' : 'rgba(171,167,154,0.7)',
        ...style,
      }}
      {...rest}
    >
      {text.length === 2 ? number + ' — ' + children : text[0]}
    </div>
  );
}
