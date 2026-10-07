import * as React from 'react';

/**
 * Шапка сайта: знак — навигация — телефон. Прозрачная поверх hero, Ink при скролле.
 *
 * @startingPoint section="Сайт" subtitle="Шапка сайта с навигацией и телефоном" viewport="1200x120"
 */
export interface SiteHeaderProps {
  /** Пункты навигации в порядке макета */
  items?: string[];
  /** Активный пункт — выводится на 90% непрозрачности */
  active?: string;
  /** Телефон капителью справа */
  phone?: string;
  /** transparent — поверх фото/видео, ink — залитая при скролле, brand — поверх Terra */
  surface?: 'transparent' | 'ink' | 'brand';
  onNavigate?: (item: string) => void;
  style?: React.CSSProperties;
}

export function SiteHeader(props: SiteHeaderProps): JSX.Element;
