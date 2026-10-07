import * as React from 'react';

/**
 * Карточка сегмента: номер → название капителью → врезка курсивом → описание.
 *
 * @startingPoint section="Сайт" subtitle="Пара карточек сегментов на Slate и Terra" viewport="700x340"
 */
export interface SegmentCardProps {
  /** «01», «02» */
  number?: string;
  title?: React.ReactNode;
  /** Интонационная врезка курсивом: «для семьи и близких» */
  subtitle?: React.ReactNode;
  /** Описание сегмента — основной текст капителью */
  children?: React.ReactNode;
  /** card — Slate, brand — Terra */
  surface?: 'card' | 'brand';
  style?: React.CSSProperties;
}

export function SegmentCard(props: SegmentCardProps): JSX.Element;
