import React from 'react';
import { SectionLabel } from '../core/SectionLabel.jsx';

/* Карточка сегмента. Порядок сверху вниз всегда один:
   номер → название → врезка курсивом → описание.
   Поверх Terra прозрачность текста поднимается на шаг — фон светлее. */
export function SegmentCard({ number, title, subtitle, children, surface = 'card', style, ...rest }) {
  const onBrand = surface === 'brand';
  return (
    <article
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 22,
        minHeight: 300,
        padding: 'var(--pad-card)',
        background: onBrand ? 'var(--surface-brand)' : 'var(--surface-card)',
        borderRadius: 'var(--radius)',
        ...style,
      }}
      {...rest}
    >
      {number && <SectionLabel number={number} tone={onBrand ? 'on-brand' : 'accent'} />}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <h3
          style={{
            margin: 0,
            fontFamily: 'var(--h3-family)',
            fontWeight: 'var(--h3-weight)',
            fontSize: 40,
            lineHeight: 'var(--h3-leading)',
            letterSpacing: 'var(--h3-tracking)',
            textTransform: 'uppercase',
            color: onBrand ? 'var(--greige-90)' : 'var(--text-subtitle)',
          }}
        >
          {title}
        </h3>
        {subtitle && (
          <div
            style={{
              fontFamily: 'var(--micro-family)',
              fontStyle: 'var(--micro-style)',
              fontSize: 'var(--micro-size)',
              lineHeight: 'var(--micro-leading)',
              letterSpacing: 'var(--micro-tracking)',
              color: 'var(--greige-90)',
            }}
          >
            {subtitle}
          </div>
        )}
      </div>
      <p
        style={{
          margin: 0,
          fontFamily: 'var(--text-family)',
          fontSize: 'var(--text-size)',
          fontWeight: 'var(--text-weight)',
          lineHeight: 1.7,
          letterSpacing: 'var(--text-tracking)',
          textTransform: 'uppercase',
          color: onBrand ? 'var(--text-on-brand-body)' : 'var(--text-body)',
        }}
      >
        {children}
      </p>
    </article>
  );
}
