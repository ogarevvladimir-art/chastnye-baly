import React from 'react';

/* Поле формы: только нижняя линия, без рамок и заливок.
   Метка сверху капителью — всегда видна, плейсхолдер её не заменяет. */
export function FormField({ label, placeholder, value, onChange, state = 'rest', hint, type = 'text', name, style, ...rest }) {
  const line =
    state === 'error' ? 'var(--field-line-error)' : state === 'focus' ? 'var(--field-line-focus)' : 'var(--field-line-rest)';
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: 10, ...style }} {...rest}>
      <span
        style={{
          fontFamily: 'var(--font-sans)',
          fontSize: 'var(--label-size)',
          fontWeight: 600,
          letterSpacing: 'var(--label-tracking)',
          textTransform: 'uppercase',
          color: state === 'error' ? 'var(--color-accent)' : 'var(--greige-40)',
        }}
      >
        {label}
      </span>
      <input
        type={type}
        name={name}
        value={value}
        placeholder={placeholder}
        onChange={onChange}
        style={{
          appearance: 'none',
          background: 'transparent',
          border: 0,
          borderBottom: 'var(--border-width) solid ' + line,
          borderRadius: 'var(--radius)',
          padding: 'var(--pad-field)',
          fontFamily: 'var(--font-sans)',
          fontSize: 15,
          fontWeight: 500,
          letterSpacing: '0.3px',
          color: 'var(--greige-90)',
          outline: 'none',
          transition: 'var(--transition-hover)',
        }}
      />
      {hint && (
        <span
          style={{
            fontFamily: 'var(--font-sans)',
            fontSize: 'var(--label-size)',
            fontWeight: 500,
            letterSpacing: '0.3px',
            color: state === 'error' ? 'var(--color-accent)' : 'var(--text-muted)',
          }}
        >
          {hint}
        </span>
      )}
    </label>
  );
}
