import React from 'react';

interface TextBoxProps {
  type: 'rounded-rect' | 'rect' | 'none';
  fill?: string;
  padding?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}

export const TextBox: React.FC<TextBoxProps> = ({
  type,
  fill = 'rgba(0,0,0,0.5)',
  padding = 20,
  children,
  style,
}) => {
  if (type === 'none') return <>{children}</>;

  const boxStyle: React.CSSProperties = {
    backgroundColor: fill,
    padding: `${padding}px`,
    borderRadius: type === 'rounded-rect' ? '20px' : '0px',
    display: 'inline-block',
    ...style,
  };

  return <div style={boxStyle}>{children}</div>;
};
