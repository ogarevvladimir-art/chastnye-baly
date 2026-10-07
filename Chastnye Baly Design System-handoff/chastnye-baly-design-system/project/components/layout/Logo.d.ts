import * as React from 'react';

/** Логотип «Plyaskin Events» (PNG, прозрачный фон). Знак компании; «Частные балы» — название услуги и набирается компонентом Wordmark. */
export interface LogoProps {
  /** Высота знака в px; ширина считается пропорционально. 40–56 — шапка, 88+ — титульные экраны */
  height?: number;
  /** Переопределить путь к файлу знака */
  src?: string;
  alt?: string;
  style?: React.CSSProperties;
}

export function Logo(props: LogoProps): JSX.Element;
