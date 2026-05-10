/**
 * Safe Grapheme Splitter
 * Uses Intl.Segmenter if available (recommended for Bangla support),
 * falls back to basic array conversion.
 */
export const splitIntoGraphemes = (text: string): string[] => {
  if (typeof Intl !== "undefined" && (Intl as any).Segmenter) {
    const segmenter = new (Intl as any).Segmenter("bn", {
      granularity: "grapheme"
    });
    return Array.from(segmenter.segment(text)).map(
      (s: any) => s.segment
    );
  }
  return Array.from(text);
};

/**
 * Detects the font to use for a given character.
 * We prioritize English font for typical Latin characters and punctuation.
 * Everything else (including Bangla) defaults to the Bangla font.
 */
export const getFontForChar = (char: string): "EnglishFont" | "BanglaFont" => {
  // English letters, numbers, and common symbols/punctuation
  // We use a regex that specifically targets English alphanumeric and standard punctuation.
  if (/[a-zA-Z0-9]/.test(char)) {
    return "EnglishFont";
  }

  // Standard punctuation/symbols that should use English font
  if (/[\s\.,!\?\(\)\[\]\{\}:;'"_&%\$#@\*=\+\-\/\\<>|\|]/.test(char)) {
    return "EnglishFont";
  }

  // Default to Bangla for characters outside the Latin-1 range (like Bangla characters)
  return "BanglaFont";
};

/**
 * Splits text into words while preserving spaces for animation.
 */
export const splitIntoWords = (text: string): string[] => {
    return text.split(/(\s+)/).filter(Boolean);
};
