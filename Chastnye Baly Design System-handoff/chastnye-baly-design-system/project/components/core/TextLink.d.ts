import * as React from 'react';

/** Текстовая ссылка антиквой со стрелкой — вторичное действие и переход внутри текста. */
export interface TextLinkProps {
  children?: React.ReactNode;
  href?: string;
  onClick?: (e: React.MouseEvent) => void;
  /** Переопределить кегль; по умолчанию 34px (--link-size) */
  size?: string | number;
  /** Стрелка слева. Выключается только в плотных списках */
  showArrow?: boolean;
  tone?: 'default' | 'on-brand';
  style?: React.CSSProperties;
}

export function TextLink(props: TextLinkProps): JSX.Element;
