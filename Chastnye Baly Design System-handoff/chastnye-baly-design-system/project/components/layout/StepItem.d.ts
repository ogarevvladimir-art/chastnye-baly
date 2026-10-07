import * as React from 'react';

/** Шаг процесса: линия сверху, номер терракотой, название капителью, описание. Раскладка 4+4+4. */
export interface StepItemProps {
  number?: string;
  title?: React.ReactNode;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}

export function StepItem(props: StepItemProps): JSX.Element;
