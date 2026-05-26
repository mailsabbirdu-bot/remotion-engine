import React from 'react';

interface TextBoxProps {
  type: 'rounded-rect' | 'rect' | 'none';
  fill?: string;
  padding?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}

export const TextBox: React.FC<TextBoxProps & { color?: string }> = ({
  type,
  fill = 'rgba(0,0,0,0.5)',
  color, // Support 'color' key from JSON
  padding = 20,
  children,
  style,
}) => {
  const finalFill = color || fill;
  if (type === 'none') return <>{children}</>;

  const boxStyle: React.CSSProperties = {
    backgroundColor: finalFill,
    padding: `${padding}px`,
    borderRadius: type === 'rounded-rect' ? '20px' : '0px',
    display: 'inline-block',
    ...style,
  };

  return <div style={boxStyle}>{children}</div>;
};
