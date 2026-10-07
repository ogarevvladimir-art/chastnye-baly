import * as React from 'react';

/** Поле ввода: метка капителью сверху, только нижняя линия. Состояния rest / focus / error. */
export interface FormFieldProps {
  label?: React.ReactNode;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  /** rest — линия 30%, focus — линия 100% greige, error — терракота на линии и метке */
  state?: 'rest' | 'focus' | 'error';
  /** Подпись под полем: подсказка или текст ошибки */
  hint?: React.ReactNode;
  type?: string;
  name?: string;
  style?: React.CSSProperties;
}

export function FormField(props: FormFieldProps): JSX.Element;
