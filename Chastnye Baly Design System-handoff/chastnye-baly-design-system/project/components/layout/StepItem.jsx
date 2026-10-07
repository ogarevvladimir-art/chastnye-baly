import React from 'react';
import { SectionLabel } from '../core/SectionLabel.jsx';

/* Шаг подготовки: линия сверху, номер, название капителью, описание.
   Раскладка 4+4+4 в колоночной сетке. */
export function StepItem({ number, title, children, style, ...rest }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
        borderTop: 'var(--border-width) solid var(--line-section)',
        paddingTop: 'var(--space-24)',
        ...style,
      }}
      {...rest}
    >
      {number && <SectionLabel number={number} />}
      <h3
        style={{
          margin: 0,
          fontFamily: 'var(--h3-family)',
          fontWeight: 'var(--h3-weight)',
          fontSize: 34,
          lineHeight: 'var(--h3-leading)',
          letterSpacing: 'var(--h3-tracking)',
          textTransform: 'uppercase',
          color: 'var(--text-subtitle)',
        }}
      >
        {title}
      </h3>
      <p
        style={{
          margin: 0,
          fontFamily: 'var(--text-family)',
          fontSize: 'var(--text-size)',
          fontWeight: 'var(--text-weight)',
          lineHeight: 1.7,
          letterSpacing: 'var(--text-tracking)',
          textTransform: 'uppercase',
          color: 'var(--text-body)',
        }}
      >
        {children}
      </p>
    </div>
  );
}
