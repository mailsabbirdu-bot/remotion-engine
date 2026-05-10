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
 * Normalizes tokens by replacing spaces with non-breaking spaces for proper layout in some cases.
 */
export const normalizeTokens = (text: string): string[] =>
  splitIntoGraphemes(text).map((c) => (c === " " ? "\u00A0" : c));

/**
 * Detects the font to use for a given character.
 * Supports English (A-Z, a-z, 0-9, and common punctuation)
 * and defaults to Bangla font for others.
 */
export const getFontForChar = (char: string): "EnglishFont" | "BanglaFont" => {
  // English letters and numbers
  if (/[A-Za-z0-9]/.test(char)) return "EnglishFont";

  // Common punctuation and symbols used in both languages usually look fine in English fonts
  if (/[\s\.,!\?\(\)\[\]\{\}:;'"_&%\$#@\*=\+\-\/\\<>|\|]/.test(char)) return "EnglishFont";

  // Default to Bangla for everything else
  return "BanglaFont";
};

/**
 * Splits text into words while preserving spaces.
 */
export const splitIntoWords = (text: string): string[] => {
    return text.split(/(\s+)/).filter(Boolean);
};
