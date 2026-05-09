import React from 'react';
import { interpolate, useCurrentFrame, Easing } from 'remotion';
import { splitIntoWords, getFontForChar, splitIntoGraphemes } from '../utils/text-utils';

interface WordByWordTextProps {
  text: string;
  style: React.CSSProperties;
  banglaFontFamily: string;
  englishFontFamily: string;
  animationType?: string;
  duration?: number;
}

export const WordByWordText: React.FC<WordByWordTextProps> = ({
  text,
  style,
  banglaFontFamily,
  englishFontFamily,
  animationType = 'fade',
  duration = 30,
}) => {
  const frame = useCurrentFrame();
  const words = splitIntoWords(text);

  return (
    <div style={{ ...style, display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
      {words.map((word, wordIndex) => {
        const graphemes = splitIntoGraphemes(word);

        // Simple word-based animation timing
        const delay = (wordIndex / words.length) * duration;
        const opacity = interpolate(
          frame,
          [delay, delay + 5],
          [0, 1],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        );

        return (
          <span key={wordIndex} style={{ opacity, display: 'inline-block', whiteSpace: 'pre' }}>
            {graphemes.map((char, charIndex) => {
              const fontType = getFontForChar(char);
              const fontFamily = fontType === 'BanglaFont' ? banglaFontFamily : englishFontFamily;
              return (
                <span key={charIndex} style={{ fontFamily }}>
                  {char}
                </span>
              );
            })}
          </span>
        );
      })}
    </div>
  );
};
