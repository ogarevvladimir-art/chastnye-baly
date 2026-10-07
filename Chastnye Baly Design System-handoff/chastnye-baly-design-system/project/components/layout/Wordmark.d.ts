import * as React from 'react';

/** Словесный знак «Частные балы» антиквой. Логотипа-файла в исходниках нет — знак набирается типографикой. */
export interface WordmarkProps {
  /** Кегль в px. 24 — шапка и футер, 60+ — титульные экраны */
  size?: number;
  tone?: 'default' | 'on-brand';
  style?: React.CSSProperties;
}

export function Wordmark(props: WordmarkProps): JSX.Element;
