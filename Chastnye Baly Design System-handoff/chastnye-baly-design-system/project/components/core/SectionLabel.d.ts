import * as React from 'react';

/** Метка секции или номер шага: «01 — ПОДГОТОВКА», «02». Терракота, трекинг 2.34px. */
export interface SectionLabelProps {
  /** Номер: «01», «3.5» */
  number?: string;
  /** Название секции капителью. Без него выводится только номер */
  children?: React.ReactNode;
  /** accent — терракота на тёмном; on-brand — greige 70% поверх Terra */
  tone?: 'accent' | 'on-brand';
  style?: React.CSSProperties;
}

export function SectionLabel(props: SectionLabelProps): JSX.Element;
