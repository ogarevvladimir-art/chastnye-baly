import * as React from 'react';

/**
 * Финальная полоса на Terra: метка секции, заголовок капителью, кнопка справа.
 *
 * @startingPoint section="Сайт" subtitle="Финальная полоса-призыв на Terra" viewport="1200x400"
 */
export interface CTABandProps {
  /** Название секции капителью: «СВЯЗАТЬСЯ» */
  label?: React.ReactNode;
  number?: string;
  title?: React.ReactNode;
  /** Надпись на кнопке */
  action?: React.ReactNode;
  onAction?: (e: React.MouseEvent) => void;
  style?: React.CSSProperties;
}

export function CTABand(props: CTABandProps): JSX.Element;
