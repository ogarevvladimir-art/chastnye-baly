import * as React from 'react';

/**
 * Полоса-передышка: врезка курсивом и крупная фраза антиквой по центру. По умолчанию на Ash.
 *
 * @startingPoint section="Сайт" subtitle="Полоса-передышка с фразой антиквой" viewport="1200x360"
 */
export interface QuoteBandProps {
  /** Врезка курсивом над фразой */
  eyebrow?: React.ReactNode;
  children?: React.ReactNode;
  /** rest — Ash (по умолчанию), ink, brand — Terra */
  surface?: 'rest' | 'ink' | 'brand';
  style?: React.CSSProperties;
}

export function QuoteBand(props: QuoteBandProps): JSX.Element;
