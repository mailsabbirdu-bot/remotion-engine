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
  localFrame: number;
}

export const WordByWordText: React.FC<WordByWordTextProps> = ({
  text,
  style,
  banglaFontFamily,
  englishFontFamily,
  duration = 30,
  animationMode = 'word',
  localFrame,
}) => {
  const renderGraphemes = (graphemes: string[], globalOpacity: number = 1, individualDelays: boolean = false, startDelay: number = 0) => {
    return (
      <>
        {graphemes.map((char, index) => {
          const fontType = getFontForChar(char);
          const fontFamily = fontType === 'BanglaFont' ? `"${banglaFontFamily}"` : `"${englishFontFamily}"`;

          let opacity = globalOpacity;
          if (individualDelays) {
            const delay = startDelay + (index / graphemes.length) * duration;
            opacity = interpolate(localFrame, [delay, delay + 5], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            });
          }

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
      </>
    );
  };

  if (animationMode === 'none') {
    const graphemes = splitIntoGraphemes(text);
    return (
      <div style={{ ...style, display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
        {renderGraphemes(graphemes)}
      </div>
    );
  }

  if (animationMode === 'sentence') {
    const opacity = interpolate(localFrame, [0, duration], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
    const graphemes = splitIntoGraphemes(text);
    return (
      <div style={{ ...style, display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
        {renderGraphemes(graphemes, opacity)}
      </div>
    );
  }

  if (animationMode === 'character') {
    const graphemes = splitIntoGraphemes(text);
    return (
      <div style={{ ...style, display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
        {renderGraphemes(graphemes, 1, true)}
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
        const opacity = interpolate(localFrame, [delay, delay + 5], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });

        return (
          <span key={wordIndex} style={{ display: 'inline-block', whiteSpace: 'pre' }}>
            {renderGraphemes(graphemes, opacity)}
          </span>
        );
      })}
    </div>
  );
};
