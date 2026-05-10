import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { getFontForChar, splitIntoGraphemes } from '../utils/text-utils';

export type TextAnimationMode = 'word' | 'character' | 'sentence' | 'none';

interface WordByWordTextProps {
  text: string;
  style: React.CSSProperties;
  banglaFontFamily: string;
  englishFontFamily: string;
  duration?: number;
  animationMode?: TextAnimationMode;
}

export const WordByWordText: React.FC<WordByWordTextProps> = ({
  text,
  style,
  banglaFontFamily,
  englishFontFamily,
  duration = 30,
  animationMode = 'word',
}) => {
  const frame = useCurrentFrame();

  if (animationMode === 'none') {
    const graphemes = splitIntoGraphemes(text);
    return (
      <div style={{ ...style, display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
        {graphemes.map((char, charIndex) => {
          const fontType = getFontForChar(char);
          const fontFamily = fontType === 'BanglaFont' ? banglaFontFamily : englishFontFamily;
          return (
            <span key={charIndex} style={{ fontFamily, whiteSpace: char === ' ' ? 'pre' : 'normal' }}>
              {char}
            </span>
          );
        })}
      </div>
    );
  }

  if (animationMode === 'sentence') {
    const opacity = interpolate(frame, [0, duration], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
    const graphemes = splitIntoGraphemes(text);
    return (
      <div style={{ ...style, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', opacity }}>
        {graphemes.map((char, charIndex) => {
          const fontType = getFontForChar(char);
          const fontFamily = fontType === 'BanglaFont' ? banglaFontFamily : englishFontFamily;
          return (
            <span key={charIndex} style={{ fontFamily, whiteSpace: char === ' ' ? 'pre' : 'normal' }}>
              {char}
            </span>
          );
        })}
      </div>
    );
  }

  if (animationMode === 'character') {
    const graphemes = splitIntoGraphemes(text);
    return (
      <div style={{ ...style, display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
        {graphemes.map((char, index) => {
          const fontType = getFontForChar(char);
          const fontFamily = fontType === 'BanglaFont' ? banglaFontFamily : englishFontFamily;

          const delay = (index / graphemes.length) * duration;
          const opacity = interpolate(frame, [delay, delay + 5], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });

          return (
            <span
              key={index}
              style={{
                fontFamily,
                opacity,
                display: 'inline-block',
                whiteSpace: char === ' ' ? 'pre' : 'normal',
              }}
            >
              {char}
            </span>
          );
        })}
      </div>
    );
  }

  // Default: Word-by-word
  const words = text.split(/(\s+)/).filter(Boolean);
  return (
    <div style={{ ...style, display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
      {words.map((word, wordIndex) => {
        const graphemes = splitIntoGraphemes(word);
        const delay = (wordIndex / words.length) * duration;
        const opacity = interpolate(frame, [delay, delay + 5], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });

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
