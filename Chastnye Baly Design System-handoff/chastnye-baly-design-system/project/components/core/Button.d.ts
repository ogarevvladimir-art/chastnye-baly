import * as React from 'react';

/**
 * Основная кнопка системы — обводка greige, без заливки, без скруглений.
 * Одна на экран. Hover инвертирует заливку и цвет текста.
 *
 * @startingPoint section="Основы" subtitle="Кнопка и текстовая ссылка" viewport="700x200"
 */
export interface ButtonProps {
  children?: React.ReactNode;
  /** md — 17px 34px (базовая), lg — 19px 38px (финальный CTA) */
  size?: 'md' | 'lg';
  /** Переопределить тег: по умолчанию button, либо a при заданном href */
  as?: keyof JSX.IntrinsicElements;
  href?: string;
  disabled?: boolean;
  onClick?: (e: React.MouseEvent) => void;
  style?: React.CSSProperties;
}

export function Button(props: ButtonProps): JSX.Element;
